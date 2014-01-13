#!/usr/bin/env python

## Program:   VMTK
## Module:    $RCSfile: vmtkpathlineanimator.py,v $
## Language:  Python
## Date:      $Date: 2013/07/09 16:10:27 $
## Version:   $Revision: 1.6 $

##   Copyright (c) Luca Antiga, David Steinman. All rights reserved.
##   See LICENCE file for details.

##      This software is distributed WITHOUT ANY WARRANTY; without even 
##      the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
##      PURPOSE.  See the above copyright notices for more information.

## Note: this class was contributed by 
##       Simone Manini
##       Orobix Srl

import vtk
import sys
import os

import vtkvmtk
import vmtkrenderer
import vmtksurfaceviewer
import pypes

vmtkpathlineanimator = 'vmtkPathLineAnimator'

class vmtkPathLineAnimator(pypes.pypeScript):

    def __init__(self):

        pypes.pypeScript.__init__(self)

        self.InputTraces = None
        self.vmtkRenderer = None
        self.OwnRenderer = 0
        self.ArrayName = "Velocity"
        self.Pattern = "frame_%04d.png"
        self.ImagesDirectory = os.getenv("HOME") 
        self.MinTime = 0.0
        self.MaxTime = 1.0
        self.Legend = 0
        self.TimeStep = None
        self.StreakLineTimeLength = 0.01
        self.WithScreenshots = 0
        self.ArrayMax = None
        self.ArrayUnit = 'cm/s'
        self.PointSize = 6
        self.LineWidth = 2
        self.Method = 'particles' 
        self.Traces = None

        self.SetScriptName('vmtkpathlineanimator')
        self.SetScriptDoc('Particle or streaklines animation')
        
        self.SetInputMembers([
            ['InputTraces','i','vtkPolyData',1,'','traces', 'vmtksurfacereader'],
            ['vmtkRenderer','renderer','vmtkRenderer',1,'','external renderer'],
            ['Method','method','str',1,'["particles","streaklines"]','animator method'],
            ['StreakLineTimeLength','streaklinetimelength','float',1,'(0.0,)'],
            ['Legend','legend','bool',1,'','toggle scalar bar'],
            ['MinTime','mintime','float',1,'(0.0,)'],
            ['MaxTime','maxtime','float',1,'(0.0,)'],
            ['TimeStep','timestep','float',1,'(0.0,)'],
            ['Pattern','pattern','str',1,''],
            ['ImagesDirectory','imagesdirectory','str',1,''],
            ['WithScreenshots','screenshot','bool',1,''],
            ['ArrayMax','arraymax','float',1,'(0.0,)'],
            ['ArrayUnit','arrayunit','str',1,'', 'array unit measure'],
            ['PointSize','pointsize','int',1,'(1,)'],
            ['LineWidth','linewidth','int',1,'(1,)'],
            ['ArrayName','array','str',1,'','name of the array where the scalars to be displayed are stored'],
            ])
        self.SetOutputMembers([
            ])

    def Screenshot(self, surfaceViewer, timestep):        
        
        fileName = self.Pattern%timestep
        homeDir = self.ImagesDirectory	
        windowToImage = vtk.vtkWindowToImageFilter()
        windowToImage.SetInput(surfaceViewer.vmtkRenderer.RenderWindow)
        windowToImage.SetMagnification(surfaceViewer.vmtkRenderer.ScreenshotMagnification)
        windowToImage.Update()
        surfaceViewer.vmtkRenderer.RenderWindow.Render()
        writer = vtk.vtkPNGWriter()
        writer.SetInput(windowToImage.GetOutput())
        writer.SetFileName(os.path.join(homeDir,fileName))
        writer.Write()

    def Execute(self):
            
        if (self.InputTraces == None):
            self.PrintError('Error: no Traces.')
        
        if (self.TimeStep == None):
            self.PrintError('Error: no TimeStep.')
        
        if not self.vmtkRenderer:
            self.vmtkRenderer = vmtkrenderer.vmtkRenderer()
            self.vmtkRenderer.Initialize()
            self.OwnRenderer = 1
        
        surfaceViewer = vmtksurfaceviewer.vmtkSurfaceViewer()
        surfaceViewer.vmtkRenderer = self.vmtkRenderer
        surfaceViewer.Surface = self.InputTraces
        surfaceViewer.ArrayName = self.ArrayName
        surfaceViewer.Execute()

        lut = vtk.vtkLookupTable()
        lut.SetHueRange(0.666667,0.0)
        lut.SetSaturationRange(0.75,0.75)
        lut.SetValueRange(1.0,1.0)
        lut.SetAlphaRange(1.0,1.0)
        lut.SetNumberOfColors(256)
        lut.Build()
        surfaceViewer.Actor.GetMapper().SetLookupTable(lut)
                
        if (self.Legend == 1):
            self.ScalarBarActor = vtk.vtkScalarBarActor()
            self.ScalarBarActor.SetLookupTable(surfaceViewer.Actor.GetMapper().GetLookupTable())
            self.ScalarBarActor.GetLabelTextProperty().ItalicOff()
            self.ScalarBarActor.GetLabelTextProperty().BoldOff()
            self.ScalarBarActor.GetLabelTextProperty().ShadowOff()
            self.ScalarBarActor.SetWidth(0.1)
            self.ScalarBarActor.SetHeight(0.6)
            self.ScalarBarActor.SetNumberOfLabels(4)
            self.ScalarBarActor.SetTitle(self.ArrayName+" ["+self.ArrayUnit+"]")
            self.ScalarBarActor.SetLabelFormat('%.2f')
            self.vmtkRenderer.Renderer.AddActor(self.ScalarBarActor)
       
        self.Traces = vtk.vtkPolyData()
        self.Traces.DeepCopy(self.InputTraces) 
        self.Traces.GetPointData().SetActiveScalars("IntegrationTime")
        timeRange = self.Traces.GetPointData().GetScalars().GetRange(0)
        currentCycle = 0
        minTime = self.MinTime
        currentTime = self.TimeStep 
        maxTime = self.MaxTime
        if (self.ArrayMax == None and self.ArrayName == "Velocity"):
            self.ArrayMax = round(self.Traces.GetPointData().GetArray('Speed').GetRange()[1],0)
        
        if self.Method is 'particles':
            particleTime = minTime
            imageNumber = 0
            while particleTime <= maxTime:
                contour = vtk.vtkContourFilter()
                contour.SetInput(self.Traces)
                i = 0
                while i <= currentCycle:
                    time = minTime + currentTime + (maxTime - minTime) * i
                    if time < timeRange[0] or time > timeRange[1]:
                        pass
                    else:
                        contour.SetValue(i,time)
                    i+=1
                
                contour.Update()
                surfaceViewer.vmtkRenderer = self.vmtkRenderer
                surfaceViewer.Actor.GetProperty().SetPointSize(self.PointSize)
                vtk.vtkPolyDataMapper.SafeDownCast(surfaceViewer.Actor.GetMapper()).SetInput(contour.GetOutput())       
                
                surfaceViewer.Actor.GetMapper().GetLookupTable().SetVectorModeToMagnitude() 
                surfaceViewer.Actor.GetMapper().SetScalarModeToUsePointFieldData() 
                surfaceViewer.Actor.GetMapper().SelectColorArray(self.ArrayName) 
                surfaceViewer.Actor.GetMapper().SetScalarRange([0.0,self.ArrayMax]) 
                        
                surfaceViewer.vmtkRenderer.RenderWindow.Render()
                if self.WithScreenshots:
                    self.Screenshot(surfaceViewer,imageNumber)
                
                particleTime+=self.TimeStep
                currentTime+=self.TimeStep
                imageNumber+=1

        elif self.Method is 'streaklines':
            particleTime = minTime
            imageNumber = 0
            while particleTime <= maxTime:
                clip1 = vtk.vtkClipPolyData()
                clip1.SetInput(self.Traces)
                clip1.GenerateClipScalarsOff()
                clip1.InsideOutOn()
                clip2 = vtk.vtkClipPolyData()
                clip2.SetInput(clip1.GetOutput())
                clip2.GenerateClipScalarsOff()
                clip2.InsideOutOff()

                cyclesPerRange = (int((timeRange[1]-timeRange[0])/(maxTime-minTime))) + 1
                cycle = currentCycle % cyclesPerRange
                time = minTime + currentTime + (maxTime - minTime) * cycle
                streakLineTimeLength = self.StreakLineTimeLength

                clip1.SetValue(time)
                clip2.SetValue(time - streakLineTimeLength)
                clip2.Update()
            
                surfaceViewer.Actor.GetProperty().SetLineWidth(self.LineWidth)
                vtk.vtkPolyDataMapper.SafeDownCast(surfaceViewer.Actor.GetMapper()).SetInput(clip2.GetOutput())
                
                surfaceViewer.Actor.GetMapper().GetLookupTable().SetVectorModeToMagnitude() 
                surfaceViewer.Actor.GetMapper().SetScalarModeToUsePointFieldData() 
                surfaceViewer.Actor.GetMapper().SelectColorArray(self.ArrayName) 
                surfaceViewer.Actor.GetMapper().SetScalarRange([0.0,self.ArrayMax]) 
                
                surfaceViewer.vmtkRenderer = self.vmtkRenderer
                surfaceViewer.vmtkRenderer.RenderWindow.Render()
                if self.WithScreenshots:
                    self.Screenshot(surfaceViewer,imageNumber)
                
                particleTime+=self.TimeStep
                currentTime+=self.TimeStep
                imageNumber+=1
        else:
            self.PrintError('Error: pathlineanimator  method not supported.')

if __name__=='__main__':
    main = pypes.pypeMain()
    main.Arguments = sys.argv
    main.Execute()