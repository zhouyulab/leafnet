
importClass(Packages.de.unihalle.informatik.MiToBo.apps.cellMorphology.PaCeQuant)
importClass(Packages.de.unihalle.informatik.Alida.datatypes.ALDDirectoryString)

// Get PaceQuant object and reflect objects
var pc_obj = new PaCeQuant()
var pc_class = pc_obj.getClass()
var pc_fields = pc_class.getDeclaredFields()
var pc_methods = pc_class.getDeclaredMethods()

// Get fields and methods, make them accessible
var field_dict = new Array
var method_dict = new Array

for (var i = 0; i < pc_fields.length; i++)
{
	pc_fields[i].setAccessible(true)
	field_dict[pc_fields[i].getName()] = pc_fields[i]
}

for (var i = 0; i < pc_methods.length; i++)
{
	pc_methods[i].setAccessible(true)
	method_dict[pc_methods[i].getName()] = pc_methods[i]
}

// Use PaceQuant through reflection instead of GUI
// Select phases to run
field_dict["phasesToRun"].set(pc_obj, PaCeQuant.OperatorPhasesToRun.FEATURES_ONLY)
method_dict["switchPhaseConfigParameters"].invoke(pc_obj)
// Select segmentation input to ROI file
field_dict["segmentationInputFormat"].set(pc_obj, PaCeQuant.SegmentationInputFormat.BINARY_IMAGE)
method_dict["switchSegmentationFormatParameter"].invoke(pc_obj)
// Set operation mode to batch mode
field_dict["opMode"].set(pc_obj, PaCeQuant.OperationMode.BATCH)
method_dict["switchOpModeParameters"].invoke(pc_obj)
// Set input directory to our input dir
field_dict["inDir"].set(pc_obj, new ALDDirectoryString(input_path))
// Set pixel calibration value
field_dict["pixCalibMode"].set(pc_obj, PaCeQuant.PixelCalibration.USER)
method_dict["switchPixelCalibParameters"].invoke(pc_obj)
// Set pixel length
field_dict["pixelLengthXY"].set(pc_obj, 1/image_res)
// Set output unit
field_dict["unitXY"].set(pc_obj, PaCeQuant.MeasurementUnits.MICRONS)
// Execute
method_dict["operate"].invoke(pc_obj)

