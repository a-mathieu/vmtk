/*=========================================================================

Program:   VMTK
Module:    $RCSfile: vtkvmtkAnisotropicDiffusionImageFilter.h,v $
Language:  C++
Date:      $Date: 2006/04/06 16:48:25 $
Version:   $Revision: 1.2 $

  Copyright (c) Luca Antiga, David Steinman. All rights reserved.
  See LICENCE file for details.

  Portions of this code are covered under the VTK copyright.
  See VTKCopyright.txt or http://www.kitware.com/VTKCopyright.htm 
  for details.

  Portions of this code are covered under the ITK copyright.
  See ITKCopyright.txt or http://www.itk.org/HTML/Copyright.htm
  for details.

     This software is distributed WITHOUT ANY WARRANTY; without even 
     the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
     PURPOSE.  See the above copyright notices for more information.

=========================================================================*/

// .NAME vtkvmtkAnisotropicDiffusionImageFilter.h - Wrapper class around itk::vtkvmtkAnisotropicDiffusionImageFilter
// .SECTION Description
// vtkvmtkAnisotropicDiffusionImageFilter.h


#ifndef __vtkvmtkAnisotropicDiffusionImageFilter_h
#define __vtkvmtkAnisotropicDiffusionImageFilter_h

#include "vtkSimpleImageToImageFilter.h"
#include "vtkvmtkWin32Header.h"

class VTK_VMTK_SEGMENTATION_EXPORT vtkvmtkAnisotropicDiffusionImageFilter : public vtkSimpleImageToImageFilter
{
 public:
  static vtkvmtkAnisotropicDiffusionImageFilter *New();
  vtkTypeMacro(vtkvmtkAnisotropicDiffusionImageFilter, vtkSimpleImageToImageFilter);

  vtkGetMacro(NumberOfIterations,int);
  vtkSetMacro(NumberOfIterations,int);

  vtkGetMacro(TimeStep,double);
  vtkSetMacro(TimeStep,double);

  vtkGetMacro(Conductance,double);
  vtkSetMacro(Conductance,double);


protected:

  vtkvmtkAnisotropicDiffusionImageFilter();
  ~vtkvmtkAnisotropicDiffusionImageFilter() {};

  virtual void SimpleExecute(vtkImageData* input, vtkImageData* output) VTK_OVERRIDE;

private:
  template< class TImage >
  int FilterImage( vtkImageData*, vtkImageData*, typename TImage::Pointer );
  
  template< int VDimension >
  int FilterScalarImage( vtkImageData* , vtkImageData* , int );
  
  vtkvmtkAnisotropicDiffusionImageFilter(const vtkvmtkAnisotropicDiffusionImageFilter&);  // Not implemented.
  void operator=(const vtkvmtkAnisotropicDiffusionImageFilter&);  // Not implemented.

  int NumberOfIterations;
  double TimeStep;
  double Conductance;
  
};

#endif

