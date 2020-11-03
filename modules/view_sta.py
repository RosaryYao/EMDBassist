# -*- coding: utf-8 -*-
"""
view_sta - 3D Visualisation of a STA

This module reads in the combined data output from combine_modules and displays
- the original map file
- the subtomogram average in its original position
- the individual transformed subtomogram averages according to the transforms

Using this module is simple. By default you must provide the data file as input. It assumes
that each transform begins with a digit and is comma-separated including the last
row of the transform. An example (rm_1305.txt) is provided.

Simple Example (see Full Example below):
python view_sta.py rm_1305.txt

Other options (python view_sta.py -h)
usage: view_sta [-h] [-m MAP_FILE] [-c CONTOUR_LEVEL] [-v VOXEL_SIZE VOXEL_SIZE VOXEL_SIZE] [-O ORIGIN_INDEX ORIGIN_INDEX ORIGIN_INDEX] input_file

visualisation results of STA in the original volume

positional arguments:
  input_file            file containing transformed particles and STA

optional arguments:
  -h, --help            show this help message and exit
  -m MAP_FILE, --map-file MAP_FILE
                        original MAP file
  -c CONTOUR_LEVEL, --contour-level CONTOUR_LEVEL
                        contour level used to generate the isosurface [default: 1.0]
  -v VOXEL_SIZE VOXEL_SIZE VOXEL_SIZE, --voxel-size VOXEL_SIZE VOXEL_SIZE VOXEL_SIZE
                        voxel sizes in x, y and z [default: 1.0 1.0 1.0]
  -O ORIGIN_INDEX ORIGIN_INDEX ORIGIN_INDEX, --origin-index ORIGIN_INDEX ORIGIN_INDEX ORIGIN_INDEX
                        the origin index; can be any triple of integers [default: 0, 0, 0]

Full Example:
python view_sta.py rm_1305.txt -m emd_1305.map -c 1.14 -v 5.43 5.43 5.43 -O -162 -162 -162

"""
import argparse
import base64
import os
import re
import struct
import sys

import mrcfile
import numpy
import vtk
import vtk.util.numpy_support


def display(volumes, args):
    """Display the volumes provided in the iterable

    This function relies on VTK to do the visualisation.

    :param list volumes: a list of either MAP, STA or TransformedSTA object
    :param args: command-line arguments
    :type args: argparse.Namespace
    """
    # display data
    # create an actor for each datum
    actors = list()
    for volume in volumes:
        # source
        vol = vtk.vtkImageData()
        z_size, y_size, x_size = volume.data.shape
        x_origin, y_origin, z_origin = volume.origin
        # this is a weirdly complex calculation
        # suppose I have a distance of size D (distance)
        # the index of the first position is S (start)
        # the index of the last position is E (end)
        # the relationship between these three values is
        # E - S + 1 = D
        # therefore, E = D + S - 1
        vol.SetExtent(
            x_origin, x_size + x_origin - 1,
            y_origin, y_size + y_origin - 1,
            z_origin, z_size + z_origin - 1,
        )
        vol.SetOrigin(x_origin, y_origin, z_origin)
        sp_x = volume.x_voxel_size
        sp_y = volume.y_voxel_size
        sp_z = volume.z_voxel_size
        vol.SetSpacing(sp_x, sp_y, sp_z)
        vol.AllocateScalars(vtk.VTK_FLOAT, 1)
        # voxel data
        print(f"Inserting voxel data...", end="")
        # numpy to vtk; https://pyscience.wordpress.com/2014/09/06/numpy-to-vtk-converting-your-numpy-arrays-to-vtk-arrays-and-files/
        voxels = vtk.util.numpy_support.numpy_to_vtk(volume.data.ravel(), deep=1, array_type=vtk.VTK_FLOAT)
        print(f"done!")
        vol.GetPointData().SetScalars(voxels)
        # contour
        contours = vtk.vtkContourFilter()
        contours.SetInputData(vol)
        contours.SetValue(0, args.contour_level)
        contours.Update()
        contoursOutput = contours.GetOutput()
        # data
        obj = vtk.vtkPolyData()
        obj.SetPoints(contoursOutput.GetPoints())
        obj.SetPolys(contoursOutput.GetPolys())
        # mapper
        mapper = vtk.vtkOpenGLPolyDataMapper()
        mapper.SetInputData(obj)
        # actor & transform
        actor = vtk.vtkOpenGLActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(volume.colour)
        actor.GetProperty().SetOpacity(volume.opacity)
        if isinstance(volume, TransformedSTA):
            transform = vtk.vtkTransform()
            matrix = vtk.vtkMatrix4x4()
            for i in range(4):
                for j in range(4):
                    matrix.SetElement(i, j, volume.transform[i, j])
            transform.SetMatrix(matrix)
            print(transform)
            actor.SetUserTransform(transform)
        actors += [actor]
    # renderer
    renderer = vtk.vtkOpenGLRenderer()
    [renderer.AddActor(actor) for actor in actors]
    # cube axes
    cubeAxesActor = vtk.vtkCubeAxesActor()
    cubeAxesActor.SetBounds(renderer.ComputeVisiblePropBounds())
    cubeAxesActor.SetCamera(renderer.GetActiveCamera())
    cubeAxesActor.SetFlyMode(4)
    cubeAxesActor.SetFlyModeToStaticEdges()  # how the cube axes will appear
    cubeAxesActor.GetTitleTextProperty(0).SetColor(1.0, 1.0, 1.0)
    cubeAxesActor.GetTitleTextProperty(1).SetColor(1.0, 1.0, 1.0)
    cubeAxesActor.GetTitleTextProperty(2).SetColor(1.0, 1.0, 1.0)
    cubeAxesActor.XAxisMinorTickVisibilityOff()
    cubeAxesActor.YAxisMinorTickVisibilityOff()
    cubeAxesActor.ZAxisMinorTickVisibilityOff()
    renderer.AddActor(cubeAxesActor)
    # rendererwindow
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    # render window interactor
    render_window_interactor = vtk.vtkRenderWindowInteractor()
    render_window_interactor.SetRenderWindow(render_window)
    render_window_interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    axes_actor = vtk.vtkAxesActor()
    axes_widget = vtk.vtkOrientationMarkerWidget()
    axes_widget.SetOrientationMarker(axes_actor)
    axes_widget.SetViewport(0, 0, 0.2, 0.2)
    axes_widget.SetInteractor(render_window_interactor)
    axes_widget.SetEnabled(1)
    renderer.ResetCamera()
    # display
    render_window_interactor.Initialize()
    render_window_interactor.Start()
    return os.EX_OK


def _get_colour_and_opacity(colour_str):
    """Helper function to compute rgba values from a hexstring

    Hex strings are mainly used in browsers to set colours and opacity.

    Example:
        #ff0000 = red

    See https://www.w3schools.com/colors/colors_picker.asp for more examples
    """
    colour_m = re.match(r'^[#](?P<red>..)(?P<green>..)(?P<blue>..)(?P<alpha>..)*', colour_str)
    if colour_m:
        colour = (
            int(colour_m.group('red'), base=16) / 255,
            int(colour_m.group('green'), base=16) / 255,
            int(colour_m.group('blue'), base=16) / 255,
        )
        if colour_m.group('alpha'):
            opacity = int(colour_m.group('alpha'), base=16) / 255
        else:
            opacity = 1.0
    else:
        colour = (1.0, 0.0, 0.0)
        opacity = 0.5
    return colour, opacity


class STA:
    """Class that captures data from the output file in an integrated way"""
    def __init__(self, fn, colour, args):
        self.fn = fn
        self.args = args
        self.colour, self.opacity = _get_colour_and_opacity(colour)
        self.txs, self.mode, self.cols, self.rows, self.sections, self.raw_data = self._get_data(fn)
        self.origin = args.origin_index
        self.voxel_size = args.voxel_size

    def _get_data(self, fn):
        """Parse the file"""
        with open(fn) as f:
            txs = list()
            for row in f:
                if re.match(r'^\d', row, re.IGNORECASE):
                    tx_m = re.match(r'\d+,(?P<tx>.*)', row.strip())
                    txs += [numpy.array(list(map(float, tx_m.group('tx').split(',')))).reshape(4, 4)]
                elif re.match(r'^Mode', row, re.IGNORECASE):
                    mode_m = re.match(r'^Mode:\t(?P<mode>\d+)', row.strip())
                    mode = mode_m.group('mode')
                elif re.match(r'^Nc', row, re.IGNORECASE):
                    col_m = re.match(r'^Nc:\s+(?P<cols>\d+)', row.strip())
                    cols = int(col_m.group('cols'))
                elif re.match(r'^Nr', row, re.IGNORECASE):
                    row_m = re.match(r'^Nr:\s+(?P<rows>\d+)', row.strip())
                    rows = int(row_m.group('rows'))
                elif re.match(r'^Ns', row, re.IGNORECASE):
                    sections_m = re.match(r'^Ns:\s+(?P<sections>\d+)', row.strip())
                    sections = int(sections_m.group('sections'))
                elif re.match(r'^Data', row, re.IGNORECASE):
                    data_m = re.match(r'^Data:\s+(?P<data>[+/=\w]+)', row.strip())
                    raw_data = data_m.group('data')
        return txs, mode, cols, rows, sections, raw_data

    @property
    def x_voxel_size(self):
        return self.voxel_size[0]

    @property
    def y_voxel_size(self):
        return self.voxel_size[1]

    @property
    def z_voxel_size(self):
        return self.voxel_size[2]

    @property
    def num_voxels(self):
        return self.cols * self.rows * self.sections

    @property
    def data(self): # todo: look here
        """Decode and unpack the data"""
        bin_data = base64.b64decode(self.raw_data)
        data = struct.unpack(f"{self.num_voxels}f", bin_data)
        return numpy.array(data).reshape(self.cols, self.rows, self.sections)

    def transformed_stas(self, colour="#ff0000"):
        """The list of transformed volumes"""
        tstas = [TransformedSTA(self, tx, colour) for tx in self.txs]
        return tstas

    def __str__(self):
        return f"""Subtomogram average:
        \rTransforms ({len(self.txs)}):
        \r\t{self.txs})
        \rMode: {self.mode}
        \rSize (c,r,s): {self.cols, self.rows, self.sections}
        \rRaw data ({len(self.raw_data)}):
        \r\t{self.raw_data[:100]}
        \rLattice {self.data.shape}:
        \r\t{self.data}"""


class TransformedSTA:
    """Class capturing a transformed STA; has the same interface as MAP and STA"""
    def __init__(self, sta, transform, colour):
        self._sta = sta
        self.transform = transform
        self.colour, self.opacity = _get_colour_and_opacity(colour)
        self.mode = self._sta.mode
        self.cols = self._sta.cols
        self.rows = self._sta.rows
        self.sections = self._sta.sections
        self.raw_data = self._sta.raw_data
        self.data = self._sta.data
        self.origin = self._sta.origin
        self.voxel_size = self._sta.voxel_size
        self.x_voxel_size = self._sta.x_voxel_size
        self.y_voxel_size = self._sta.y_voxel_size
        self.z_voxel_size = self._sta.z_voxel_size
        self.num_voxels = self._sta.num_voxels

    def __str__(self):
        return f"""Transformed subtomogram average:
        \rTransform:
        \r\t{self.transform})
        \rMode: {self.mode}
        \rSize (c,r,s): {self.cols, self.rows, self.sections}
        \rRaw data ({len(self.raw_data)}):
        \r\t{self.raw_data[:100]}
        \rLattice {self.data.shape}:
        \r\t{self.data}"""


class MAP:
    """Class capturing essential attributes of a MAP"""
    def __init__(self, fn, colour, args):
        self.fn = fn
        self.args = args
        self.colour, self.opacity = _get_colour_and_opacity(colour)
        self.mode, self.cols, self.rows, self.sections, self.data, self.origin, self.voxel_size = self._get_data(fn)

    def _get_data(self, fn):
        with mrcfile.open(fn) as mrc:
            mode = mrc.header.mode
            cols = mrc.header.nx
            rows = mrc.header.ny
            sections = mrc.header.nz
            origin = mrc.header.nxstart, mrc.header.nystart, mrc.header.nzstart
            voxel_size = mrc.voxel_size
            data = mrc.data
        return mode, cols, rows, sections, data, origin, voxel_size

    @property
    def x_voxel_size(self):
        return self.voxel_size.x

    @property
    def y_voxel_size(self):
        return self.voxel_size.y

    @property
    def z_voxel_size(self):
        return self.voxel_size.z

    def __str__(self):
        return f"""EMDB MAP: {self.fn}
        \rMode: {self.mode}
        \rSize (c,r,s): {self.cols, self.rows, self.sections}
        \rLattice {self.data.shape}:
        \r\t{self.data}"""


def main():
    parser = argparse.ArgumentParser(prog='view_sta',
                                     description='visualisation results of STA in the original volume')
    parser.add_argument('input_file', help='file containing transformed particles and STA')
    parser.add_argument('-m', '--map-file', help='original MAP file')
    parser.add_argument('-c', '--contour-level', type=float, default=1.0,
                        help='contour level used to generate the isosurface [default: 1.0]')
    parser.add_argument('-v', '--voxel-size', default=[1.0, 1.0, 1.0], nargs=3, type=float,
                        help='voxel sizes in x, y and z [default: 1.0 1.0 1.0]')
    parser.add_argument('-O', '--origin-index', default=[0, 0, 0], nargs=3, type=int,
                        help='the origin index; can be any triple of integers [default: 0, 0, 0]')
    args = parser.parse_args()
    # the list of volumes to pass to display()
    volumes_to_display = list()
    # the sta output
    # NOTE: if colour is six chars then opacity = 1.0 i.e. opaque
    #   if colour is 8 chars then last two define opacity e.g. #ff000000 -> opacity = 0
    #   each pair of chars can have values in 00-ff (hexadecimal)
    sta = STA(args.input_file, '#00ffff', args) # R: light blue => the "untransformed" averaged file
    volumes_to_display += [sta]
    # the list of transformed volumes
    transformed_stas = sta.transformed_stas(colour="#ff0000") # R: Color Red
    volumes_to_display += transformed_stas
    # the original map
    if args.map_file:
        map = MAP(args.map_file, '#ffff0050', args)
        volumes_to_display += [map]
    display(volumes_to_display, args)
    return os.EX_OK


if __name__ == "__main__":
    sys.exit(main())
