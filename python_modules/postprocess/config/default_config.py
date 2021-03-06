# -*- coding: utf-8 -*-

import os
import xc_base
import geom
import xc
from postprocess import output_styles
from postprocess import limit_state_data as lsd

def findWorkingDirectory():
    '''Search upwards to find the directory where the file
       env_config.py is.'''
    working_dir= os.getcwd()
    file_name= 'env_config.py'
    while True:
        file_list = os.listdir(working_dir)
        parent_dir = os.path.dirname(working_dir)
        if file_name in file_list:
            break
        else:
            if working_dir == parent_dir: #if dir is root dir
                working_dir= None
                break
            else:
                working_dir = parent_dir
    return working_dir

class ProjectDirTree(object):
    ''' Paths to project directories.

       :ivar intForcPath: full path of the directory where results of 
                     internal forces are placed.
       :ivar verifPath: full path of the directory where results of 
                     limit state  verifications are placed
       :ivar annexPath: full path of the directory where to place graphic and 
                     text files for the generation of the annex
    '''
    def __init__(self,intForcPath,verifPath,annexPath):
        '''
        :param intForcPath: full path of the directory where results of 
                      internal forces are placed.
        :param verifPath: full path of the directory where results of 
                      limit state  verifications are placed
        :param annexPath: full path of the directory where to place graphic and 
                      text files for the generation of the annex
                            
        '''
        #default names of files with data for FE model generation, results of
        #limit state verifications, ..
        self.workingDirectory= findWorkingDirectory()
        self.intForcPath= intForcPath
        self.verifPath= verifPath
        self.annexPath= annexPath

    def getInternalForcesResultsPath(self):
        ''' Return the path for the files that contains
            the internal forces.'''
        return self.workingDirectory+'/'+self.intForcPath
    
    def getFullVerifPath(self):
        return self.workingDirectory+'/'+self.verifPath
    def getFullReportPath(self):
        return self.workingDirectory+'/'+self.annexPath+'text/'
    def getFullGraphicsPath(self):
        return self.getFullReportPath()+'graphics/'

    def getReportSectionsFile(self):
        return self.getFullReportPath()+'sectReport.tex'
    def getReportSectionsGrPath(self):
        return self.getFullReportPath()+'sections/'

    def getReportLoadsFile(self):
        return self.getFullReportPath()+'report_loads.tex'
    def getReportLoadsGrPath(self):
        return self.getFullGraphicsPath()+'loads/'
    
    def getVerifNormStrFile(self):
        return self.getFullVerifPath()+'verifRsl_normStrsULS.py'    
    def getReportNormStrFile(self):
        return self.getFullReportPath()+'report_normStrsULS.tex'
    def getReportNormStrGrPath(self):
        return self.getFullGraphicsPath()+'normStrsULS/'
        
    def getVerifShearFile(self):
        return self.getFullVerifPath()+'verifRsl_shearULS.py'
    def getReportShearFile(self):
        return self.getFullGraphicsPath()+'report_shearULS.tex'
    def getReportShearGrPath(self):
        return self.getFullGraphicsPath()+'shearULS/'

    def getVerifCrackFreqFile(self):
        return self.getFullVerifPath()+'verifRsl_crackingSLS_freq.py'
    def getReportCrackFreqFile(self):
        return self.getFullReportPath()+'report_crackingSLS_freq.tex'
    def getReportCrackFreqGrPath(self):
        return self.getFullGraphicsPath()+'crackingSLS_freq/' 
        
    def getVerifCrackQpermFile(self):
        return self.getFullVerifPath()+'verifRsl_crackingSLS_qperm.py'
    def getReportCrackQpermFile(self):
        return self.getFullReportPath()+'report_crackingSLS_qperm.tex'
    def getReportCrackQpermGrPath(self):
        return self.getFullGraphicsPath()+'crackingSLS_qperm/' 
        
    def getVerifFatigueFile(self):
        return self.getFullVerifPath()+'verifRsl_fatigueULS.py'
    def getReportFatigueFile(self):
        return self.getFullReportPath()+'report_fatigueStrsULS.tex' 
    def getReportFatigueGrPath(self):
        return self.getFullGraphicsPath()+'fatigueStrsULS/'

    def getReportSimplLCFile(self):
        return self.getFullReportPath()+'report_resSimplLC.tex'
    def getReportSimplLCGrPath(self):
        return self.getFullGraphicsPath()+'resSimplLC/'

    def getPathList(self):
        ''' Create the project directory tree.'''
        retval= list()
        retval.append(self.getInternalForcesResultsPath())
        retval.append(self.getFullVerifPath())
        retval.append(self.getFullReportPath())
        retval.append(self.getFullGraphicsPath())
        retval.append(self.getReportSectionsFile())
        retval.append(self.getReportSectionsGrPath())
        retval.append(self.getReportLoadsFile())
        retval.append(self.getReportLoadsGrPath())
        retval.append(self.getReportNormStrGrPath())
        retval.append(self.getReportShearGrPath())
        retval.append(self.getReportCrackFreqGrPath())
        retval.append(self.getReportCrackQpermGrPath())
        retval.append(self.getReportFatigueGrPath())
        retval.append(self.getReportSimplLCGrPath())
        return retval
        
    def createTree(self):
        ''' Create the project directory tree.'''
        paths= self.getPathList()
        for pth in paths:
            if(not os.path.exists(pth)):
                os.makedirs(pth)



class EnvConfig(output_styles.OutputStyle):
    '''Generic configuration of XC environment variables.

       :ivar grWidth: size of the graphics to be included in the annex          
    '''
    def __init__(self,language,intForcPath,verifPath,annexPath,grWidth='120mm'):
        '''
        :param language: english, spanish, french 
        :param intForcPath: full path of the directory where results of 
                      internal forces are placed.
        :param verifPath: full path of the directory where results of 
                      limit state  verifications are placed
        :param annexPath: full path of the directory where to place graphic and 
                      text files for the generation of the annex
        :param grWidth: size of the graphics to be included in the annex
                            
        '''
        super(EnvConfig,self).__init__(language= language)
        #default names of files with data for FE model generation, results of
        #limit state verifications, ..
        self.projectDirTree= ProjectDirTree(intForcPath,verifPath,annexPath)

        lsd.LimitStateData.internal_forces_results_directory= intForcPath
        lsd.LimitStateData.check_results_directory= verifPath

        # self.intForcPath=intForcPath
        # self.verifPath=verifPath


        self.capTexts= self.getCaptionTextsDict()
        self.colors=setBasicColors
        self.grWidth=grWidth



#Predefined colors for sets (progressing from light to dark)

setBasicColors={
    'yellow01':xc.Vector([1,1,0]),
    'yellow02':xc.Vector([1,0.9,0]),
    'orange01':xc.Vector([1,0.8,0.5]),
    'orange02':xc.Vector([1,0.7,0]),
    'orange03':xc.Vector([1,0.6,0]),
    'pink01':xc.Vector([1,0.6,1.0]),
    'pink02':xc.Vector([1,0.2,1]),
    'pink03':xc.Vector([1,0,0.7]),
    'red01':xc.Vector([1,0.1,0.1]),
    'red02':xc.Vector([1,0.2,1]),
    'red03':xc.Vector([1,0,0]),
    'red04':xc.Vector([0.9,0,0]),
    'green01':xc.Vector([0.8,1,0.4]),
    'green02':xc.Vector([0.7,0.9,0.1]),
    'green03':xc.Vector([0.8,0.8,0.1]),
    'green04':xc.Vector([0.6,0.5,0.1]),
    'brown04':xc.Vector([0.5,0.,0.]),
    'brown03':xc.Vector([0.5,0.1,0.]),
    'brown02':xc.Vector([0.5,0.3,0.1]),
    'brown01':xc.Vector([0.6,0.3,0.]),
    'purple04':xc.Vector([0.6,0.2,1.]),
    'purple03':xc.Vector([0.7,0.2,0.7]),
    'purple02':xc.Vector([0.7,0.4,0.7]),
    'purple01':xc.Vector([0.7,0.7,0.8]),
    'blue01':xc.Vector([0.2,1.,1.]),
    'blue02':xc.Vector([0.,0.8,1]),
    'blue03':xc.Vector([0.,0.4,1]),
    'blue04':xc.Vector([0.,0.,0.9])     
  }
