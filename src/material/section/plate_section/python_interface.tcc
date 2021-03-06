//----------------------------------------------------------------------------
//  XC program; finite element analysis code
//  for structural analysis and design.
//
//  Copyright (C)  Luis Claudio Pérez Tato
//
//  XC is free software: you can redistribute it and/or modify 
//  it under the terms of the GNU General Public License as published by
//  the Free Software Foundation, either version 3 of the License, or 
//  (at your option) any later version.
//
//  This software is distributed in the hope that it will be useful, but 
//  WITHOUT ANY WARRANTY; without even the implied warranty of 
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU General Public License for more details. 
//
//
// You should have received a copy of the GNU General Public License 
// along with this program.
// If not, see <http://www.gnu.org/licenses/>.
//----------------------------------------------------------------------------
//python_interface.tcc

class_<XC::ElasticPlateBase, bases<XC::SectionForceDeformation>, boost::noncopyable >("ElasticPlateBase", no_init)
  .add_property("E", &XC::ElasticPlateBase::getE, &XC::ElasticPlateBase::setE, "Material's Young modulus.")
  .add_property("nu", &XC::ElasticPlateBase::getnu, &XC::ElasticPlateBase::setnu, "Material Poisson's ratio.")
  .add_property("h", &XC::ElasticPlateBase::getH, &XC::ElasticPlateBase::setH,"material thickness.")
   ;

typedef XC::ElasticPlateProto<8> ElasticPlateProto8;
class_<ElasticPlateProto8, bases<XC::ElasticPlateBase>, boost::noncopyable >("ElasticPlateProto8", no_init)
    ;

class_<XC::ElasticMembranePlateSection, bases<ElasticPlateProto8>, boost::noncopyable  >("ElasticMembranePlateSection", no_init)
  .add_property("rho", &XC::ElasticMembranePlateSection::getRho, &XC::ElasticMembranePlateSection::setRho)
  ;

typedef XC::ElasticPlateProto<5> ElasticPlateProto5;
class_<ElasticPlateProto5, bases<XC::ElasticPlateBase>, boost::noncopyable >("ElasticPlateProto5", no_init);
class_<XC::ElasticPlateSection, bases<ElasticPlateProto5>, boost::noncopyable >("ElasticPlateSection", no_init);

class_<XC::MembranePlateFiberSection, bases<XC::SectionForceDeformation>, boost::noncopyable >("MembranePlateFiberSection", no_init);

