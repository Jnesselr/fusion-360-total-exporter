#Author-Justin Nesselrotte
#Description-A convenient way to export all of your designs and projects in the event you suddenly find yourself in need of something like that.
from __future__ import with_statement

import adsk.core, adsk.fusion, adsk.cam, traceback

from logging import Logger, FileHandler, Formatter
from threading import Thread

import time
import os
import re



class TotalExport(object):
  def __init__(self, app):
    self.app = app
    self.ui = self.app.userInterface
    self.data = self.app.data
    self.documents = self.app.documents
    self.log = Logger("Fusion 360 Total Export")
    self.num_issues = 0
    self.was_cancelled = False
    
  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    pass

  def run(self, context):
    self.ui.messageBox(
      "Searching for and exporting files will take a while, depending on how many files you have.\n\n" \
        "You won't be able to do anything else. It has to do everything in the main thread and open and close every file.\n\n" \
          "Take an early lunch."
      )

    output_path = self._ask_for_output_path()

    if output_path is None:
      return

    file_handler = FileHandler(os.path.join(output_path, 'output.log'))
    file_handler.setFormatter(Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    self.log.addHandler(file_handler)

    self.log.info("Starting export!")

    self._export_data(output_path)

    self.log.info("Done exporting!")

    if self.was_cancelled:
      self.ui.messageBox("Cancelled!")
    elif self.num_issues > 0:
      self.ui.messageBox("The exporting process ran into {num_issues} issue{english_plurals}. Please check the log for more information".format(
        num_issues=self.num_issues,
        english_plurals="s" if self.num_issues > 1 else ""
        ))
    else:
      self.ui.messageBox("Export finished completely successfully!")

  def _export_data(self, output_path):
    progress_dialog = self.ui.createProgressDialog()
    progress_dialog.show("Exporting data!", "", 0, 1, 1)

    all_hubs = self.data.dataHubs
    for hub_index in range(all_hubs.count):
      hub = all_hubs.item(hub_index)

      self.log.info("Exporting hub \"{}\"".format(hub.name))

      all_projects = hub.dataProjects
      for project_index in range(all_projects.count):
        files = []
        project = all_projects.item(project_index)
        self.log.info("Exporting project \"{}\"".format(project.name))

        folder = project.rootFolder

        files.extend(self._get_files_for(folder))

        progress_dialog.message = "Hub: {} of {}\nProject: {} of {}\nExporting design %v of %m".format(
          hub_index + 1,
          all_hubs.count,
          project_index + 1,
          all_projects.count
        )
        progress_dialog.maximumValue = len(files)
        progress_dialog.reset()

        if not files:
          self.log.info("No files to export for this project")
          continue

        for file_index in range(len(files)):
          if progress_dialog.wasCancelled:
            self.log.info("The process was cancelled!")
            self.was_cancelled = True
            return

          file: adsk.core.DataFile = files[file_index]
          progress_dialog.progressValue = file_index + 1
          self._write_data_file(output_path, file)
        self.log.info("Finished exporting project \"{}\"".format(project.name))
      self.log.info("Finished exporting hub \"{}\"".format(hub.name))

  def _ask_for_output_path(self):
    folder_dialog = self.ui.createFolderDialog()
    folder_dialog.title = "Where should we store this export?"
    dialog_result = folder_dialog.showDialog()
    if dialog_result != adsk.core.DialogResults.DialogOK:
      return None

    output_path = folder_dialog.folder

    return output_path

  def _get_files_for(self, folder):
    files = []
    for file in folder.dataFiles:
      files.append(file)

    for sub_folder in folder.dataFolders:
      files.extend(self._get_files_for(sub_folder))
    
    return files

  def _write_data_file(self, root_folder, file: adsk.core.DataFile):
    if file.fileExtension != "f3d" and file.fileExtension != "f3z":
      self.log.info("Not exporting file \"{}\"".format(file.name))
      return

    self.log.info("Exporting file \"{}\"".format(file.name))

    try:
      document = self.documents.open(file)

      if document is None:
        raise Exception("Documents.open returned None")

      document.activate()
    except BaseException as ex:
      self.num_issues += 1
      self.log.exception("Opening {} failed!".format(file.name), exc_info=ex)
      return

    try:
      file_folder = file.parentFolder
      file_folder_path = self._name(file_folder.name)

      while file_folder.parentFolder is not None:
        file_folder = file_folder.parentFolder
        file_folder_path = os.path.join(self._name(file_folder.name), file_folder_path)

      parent_project = file_folder.parentProject
      parent_hub = parent_project.parentHub

      file_folder_path = self._take(
        root_folder,
        "Hub {}".format(self._name(parent_hub.name)),
        "Project {}".format(self._name(parent_project.name)),
        file_folder_path,
        self._name(file.name) + "." + file.fileExtension
        )

      if not os.path.exists(file_folder_path):
        self.num_issues += 1
        self.log.exception("Couldn't make root folder\"{}\"".format(file_folder_path))
        return

      self.log.info("Writing to \"{}\"".format(file_folder_path))

      fusion_document: adsk.fusion.FusionDocument = adsk.fusion.FusionDocument.cast(document)
      design: adsk.fusion.Design = fusion_document.design
      export_manager: adsk.fusion.ExportManager = design.exportManager

      file_export_path = os.path.join(file_folder_path, self._name(file.name))
      # Write f3d/f3z file
      options = export_manager.createFusionArchiveExportOptions(file_export_path)
      export_manager.execute(options)
      
      self._write_component(file_folder_path, design.rootComponent)

      self.log.info("Finished exporting file \"{}\"".format(file.name))
    except BaseException as ex:
      self.num_issues += 1
      self.log.exception("Failed while working on \"{}\"".format(file.name), exc_info=ex)
      raise
    finally:
      try:
        if document is not None:
          document.close(False)
      except BaseException as ex:
        self.num_issues += 1
        self.log.exception("Failed to close \"{}\"".format(file.name), exc_info=ex)


  def _write_component(self, component_base_path, component: adsk.fusion.Component):
    self.log.info("Writing component \"{}\" to \"{}\"".format(component.name, component_base_path))
    design = component.parentDesign
    
    output_path = os.path.join(component_base_path, self._name(component.name))

    self._write_step(output_path, component)
    self._write_stl(output_path, component)
    self._write_iges(output_path, component)

    sketches = component.sketches
    for sketch_index in range(sketches.count):
      sketch = sketches.item(sketch_index)
      self._write_dxf(os.path.join(output_path, sketch.name), sketch)

    occurrences = component.occurrences
    for occurrence_index in range(occurrences.count):
      occurrence = occurrences.item(occurrence_index)
      sub_component = occurrence.component
      sub_path = self._take(component_base_path, self._name(component.name))
      self._write_component(sub_path, sub_component)

  def _write_step(self, output_path, component: adsk.fusion.Component):
    file_path = output_path + ".stp"
    if os.path.exists(file_path):
      self.log.info("Step file \"{}\" already exists".format(file_path))
      return

    self.log.info("Writing step file \"{}\"".format(file_path))
    export_manager = component.parentDesign.exportManager

    options = export_manager.createSTEPExportOptions(output_path, component)
    export_manager.execute(options)

  def _write_stl(self, output_path, component: adsk.fusion.Component):
    file_path = output_path + ".stl"
    if os.path.exists(file_path):
      self.log.info("Stl file \"{}\" already exists".format(file_path))
      return

    self.log.info("Writing stl file \"{}\"".format(file_path))
    export_manager = component.parentDesign.exportManager

    try:
      options = export_manager.createSTLExportOptions(component, output_path)
      export_manager.execute(options)
    except BaseException as ex:
      self.log.exception("Failed writing stl file \"{}\"".format(file_path), exc_info=ex)

      if component.occurrences.count + component.bRepBodies.count + component.meshBodies.count > 0:
        self.num_issues += 1

    bRepBodies = component.bRepBodies
    meshBodies = component.meshBodies

    if (bRepBodies.count + meshBodies.count) > 0:
      self._take(output_path)
      for index in range(bRepBodies.count):
        body = bRepBodies.item(index)
        self._write_stl_body(os.path.join(output_path, body.name), body)

      for index in range(meshBodies.count):
        body = meshBodies.item(index)
        self._write_stl_body(os.path.join(output_path, body.name), body)
        
  def _write_stl_body(self, output_path, body):
    file_path = output_path + ".stl"
    if os.path.exists(file_path):
      self.log.info("Stl body file \"{}\" already exists".format(file_path))
      return

    self.log.info("Writing stl body file \"{}\"".format(file_path))
    export_manager = body.parentComponent.parentDesign.exportManager

    try:
      options = export_manager.createSTLExportOptions(body, file_path)
      export_manager.execute(options)
    except BaseException:
      # Probably an empty model, ignore it
      pass

  def _write_iges(self, output_path, component: adsk.fusion.Component):
    file_path = output_path + ".igs"
    if os.path.exists(file_path):
      self.log.info("Iges file \"{}\" already exists".format(file_path))
      return

    self.log.info("Writing iges file \"{}\"".format(file_path))

    export_manager = component.parentDesign.exportManager

    options = export_manager.createIGESExportOptions(file_path, component)
    export_manager.execute(options)

  def _write_dxf(self, output_path, sketch: adsk.fusion.Sketch):
    file_path = output_path + ".dxf"
    if os.path.exists(file_path):
      self.log.info("DXF sketch file \"{}\" already exists".format(file_path))
      return

    self.log.info("Writing dxf sketch file \"{}\"".format(file_path))

    sketch.saveAsDXF(output_path)

  def _take(self, *path):
    out_path = os.path.join(*path)
    os.makedirs(out_path, exist_ok=True)
    return out_path
  
  def _name(self, name):
    name = re.sub('[^a-zA-Z0-9 \n\.]', '', name).strip()

    if name.endswith('.stp') or name.endswith('.stl') or name.endswith('.igs'):
      name = name[0: -4] + "_" + name[-3:]

    return name

    

def run(context):
  ui = None
  try:
    app = adsk.core.Application.get()

    with TotalExport(app) as total_export:
      total_export.run(context)

  except:
    ui  = app.userInterface
    ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
