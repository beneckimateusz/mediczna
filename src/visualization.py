#!/usr/bin/env python

from pathlib import Path
import sys
# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
import vtk
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkLookupTable
from vtkmodules.vtkFiltersCore import vtkPolyDataNormals
from vtkmodules.vtkFiltersGeneral import vtkTransformPolyDataFilter
from vtkmodules.vtkFiltersSources import vtkPlaneSource
from vtkmodules.vtkIOImage import vtkMetaImageReader
from vtkmodules.vtkImagingCore import vtkImageConstantPad
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkCamera,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer,
    vtkTexture,
    vtkWindowLevelLookupTable,
)

from slice_order import SliceOrder


def get_program_parameters():
    import argparse
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('data_folder', help='The path to segmentation and volume mhd/raw files')
    parser.add_argument('volume_filename', help='e.g. volume_14')
    parser.add_argument('segmentation_filename', help='e.g segmentation_14')
    parser.add_argument('slice_number', help='e.g 1')
    args = parser.parse_args()
    return args


def main():
    args = get_program_parameters()
    data_folder = args.data_folder
    volume_filename = args.volume_filename
    segmentation_filename = args.segmentation_filename
    slice_number = int(args.slice_number)

    colors = vtkNamedColors()

    # Read the data
    path = Path(data_folder)
    if path.is_dir():
        s = ''
        fn_1 = path.joinpath(volume_filename).with_suffix('.mhd')
        if not fn_1.is_file():
            s += 'The file: {:s} does not exist.\n'.format(str(fn_1))
            print(s)
        fn_2 = path.joinpath(segmentation_filename).with_suffix('.mhd')
        if not fn_2.is_file():
            s += 'The file: {:s} does not exist.'.format(str(fn_2))
        if s:
            print(s)
            return
    else:
        print('Expected a path to dir containing .mhd volumes and segmentations')
        return

    so = SliceOrder()

    # Now create the RenderWindow, Renderer and Interactor
    ren1 = vtkRenderer()
    ren2 = vtkRenderer()
    ren3 = vtkRenderer()
    ren_win = vtkRenderWindow()
    ren_win.AddRenderer(ren1)
    ren_win.AddRenderer(ren2)
    ren_win.AddRenderer(ren3)
    ren_win.SetWindowName('TestSeg')

    iren = vtkRenderWindowInteractor()
    iren.SetRenderWindow(ren_win)

    grey_reader = vtkMetaImageReader()
    grey_reader.SetFileName(str(fn_1))
    grey_reader.Update()

    dims = grey_reader.GetOutput().GetDimensions()

    grey_padder = vtkImageConstantPad()
    grey_padder.SetInputConnection(grey_reader.GetOutputPort())
    grey_padder.SetOutputWholeExtent(0, 1023, 0, 1023, slice_number, slice_number)
    grey_padder.SetConstant(0)

    grey_plane = vtkPlaneSource()

    grey_transform = vtkTransformPolyDataFilter()
    grey_transform.SetTransform(so.get('hfsi'))
    grey_transform.SetInputConnection(grey_plane.GetOutputPort())

    grey_normals = vtkPolyDataNormals()
    grey_normals.SetInputConnection(grey_transform.GetOutputPort())
    grey_normals.FlipNormalsOff()

    wllut = vtkWindowLevelLookupTable()
    wllut.SetWindow(255)
    wllut.SetLevel(128)
    wllut.SetTableRange(0, 255)
    wllut.Build()

    grey_mapper = vtkPolyDataMapper()
    grey_mapper.SetInputConnection(grey_plane.GetOutputPort())

    grey_texture = vtkTexture()
    grey_texture.SetInputConnection(grey_padder.GetOutputPort())
    grey_texture.SetLookupTable(wllut)
    grey_texture.SetColorModeToMapScalars()
    grey_texture.InterpolateOn()

    grey_actor = vtkActor()
    grey_actor.SetMapper(grey_mapper)
    grey_actor.SetTexture(grey_texture)

    segment_reader = vtkMetaImageReader()
    segment_reader.SetFileName(str(fn_2))
    segment_reader.Update()

    segment_padder = vtkImageConstantPad()
    segment_padder.SetInputConnection(segment_reader.GetOutputPort())
    segment_padder.SetOutputWholeExtent(0, 1023, 0, 1023, slice_number, slice_number)
    segment_padder.SetConstant(0)

    segment_plane = vtkPlaneSource()

    segment_transform = vtkTransformPolyDataFilter()
    segment_transform.SetTransform(so.get('hfsi'))
    segment_transform.SetInputConnection(segment_plane.GetOutputPort())

    segment_normals = vtkPolyDataNormals()
    segment_normals.SetInputConnection(segment_transform.GetOutputPort())
    segment_normals.FlipNormalsOn()

    lut = create_lut(colors)

    segment_mapper = vtkPolyDataMapper()
    segment_mapper.SetInputConnection(segment_plane.GetOutputPort())

    segment_texture = vtkTexture()
    segment_texture.SetInputConnection(segment_padder.GetOutputPort())
    segment_texture.SetLookupTable(lut)
    segment_texture.SetColorModeToMapScalars()
    segment_texture.InterpolateOff()

    segment_actor = vtkActor()
    segment_actor.SetMapper(segment_mapper)
    segment_actor.SetTexture(segment_texture)

    segment_overlay_actor = vtkActor()
    segment_overlay_actor.SetMapper(segment_mapper)
    segment_overlay_actor.SetTexture(segment_texture)

    segment_overlay_actor.GetProperty().SetOpacity(.5)
    ren1.SetBackground(0, 0, 0)
    ren1.SetViewport(0, 0.5, 0.5, 1)
    ren_win.SetSize(900, 900)
    ren1.AddActor(grey_actor)

    ren2.SetBackground(0, 0, 0)
    ren2.SetViewport(0.5, 0.5, 1, 1)
    ren2.AddActor(segment_actor)

    cam1 = vtkCamera()
    cam1.SetViewUp(0, -1, 0)
    cam1.SetPosition(0, 0, -1)
    ren1.SetActiveCamera(cam1)
    ren1.ResetCamera()
    cam1.SetViewUp(0, -1, 0)
    cam1.SetPosition(0.0554068, -0.0596001, -2)
    cam1.SetFocalPoint(0.0554068, -0.0596001, 0)
    ren1.ResetCameraClippingRange()

    ren3.AddActor(grey_actor)
    ren3.AddActor(segment_overlay_actor)
    segment_overlay_actor.SetPosition(0, 0, -0.01)

    ren1.SetBackground(colors.GetColor3d('SlateGray'))
    ren2.SetBackground(colors.GetColor3d('SlateGray'))
    ren3.SetBackground(colors.GetColor3d('SlateGray'))

    ren3.SetViewport(0, 0, 1, 0.5)

    ren2.SetActiveCamera(ren1.GetActiveCamera())
    ren3.SetActiveCamera(ren1.GetActiveCamera())

    ren_win.Render()

    # --- slider to change frame: callback class, sliderRepresentation, slider
    class FrameCallback(object):
        def __init__(self, renWin):
            self.renWin = renWin

        def __call__(self, caller, ev):
            value = caller.GetSliderRepresentation().GetValue()
            segment_padder.SetOutputWholeExtent(-200, 511, -200, 1000, int(value), int(value))
            grey_padder.SetOutputWholeExtent(-200, 511, -200, 1000, int(value), int(value))
            self.renWin.Render()

    sliderRep = vtk.vtkSliderRepresentation2D()
    sliderRep.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
    sliderRep.GetPoint1Coordinate().SetValue(.7, .1)
    sliderRep.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
    sliderRep.GetPoint2Coordinate().SetValue(.9, .1)
    sliderRep.SetMinimumValue(0)
    sliderRep.SetMaximumValue(dims[0] - 1)
    sliderRep.SetValue(slice_number)
    sliderRep.SetTitleText("frame")

    slider = vtk.vtkSliderWidget()
    slider.SetInteractor(iren)
    slider.SetRepresentation(sliderRep)
    slider.SetAnimationModeToAnimate()
    slider.EnabledOn()
    slider.AddObserver('InteractionEvent', FrameCallback(ren_win))

    iren.Start()


def create_lut(colors):
    lut = vtkLookupTable()
    lut.SetNumberOfColors(2)
    lut.SetTableRange(0, 2)
    lut.Build()

    lut.SetTableValue(0, colors.GetColor4d('Black'))
    lut.SetTableValue(1, colors.GetColor4d('salmon'))

    return lut


if __name__ == '__main__':
    main()
