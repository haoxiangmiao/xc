//----------------------------------------------------------------------------
//  XC program; finite element analysis code
//  for structural analysis and design.
//
//  Copyright (C)  Luis Claudio Pérez Tato
//
//  This program derives from OpenSees <http://opensees.berkeley.edu>
//  developed by the  «Pacific earthquake engineering research center».
//
//  Except for the restrictions that may arise from the copyright
//  of the original program (see copyright_opensees.txt)
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
//ProcSoluControl.cc

#include "ProcSoluControl.h"
#include "domain/domain/Domain.h"
#include "ProcSolu.h"

#include "solution/analysis/ModelWrapper.h"
#include "solution/AnalysisAggregation.h"

#include "boost/any.hpp"


//! @brief Default constructor.
XC::ProcSoluControl::ProcSoluControl(ProcSolu *owr)
  : CommandEntity(owr), solu_models(this), solu_methods(this) {}


XC::ProcSolu *XC::ProcSoluControl::getProcSolu(void)
  { return dynamic_cast<ProcSolu *>(Owner()); }

const XC::ProcSolu *XC::ProcSoluControl::getProcSolu(void) const
  { return dynamic_cast<const ProcSolu *>(Owner()); }

//! @brief Return a pointer to the domain on which
//! the solution algorithm operates.
XC::Domain *XC::ProcSoluControl::getDomain(void)
  {
    ProcSolu *ps= getProcSolu();
    assert(ps); 
    return ps->getDomainPtr();
  }

//! @brief Return a pointer to the domain on which
//! the solution algorithm operates.
const XC::Domain *XC::ProcSoluControl::getDomain(void) const
  {
    const ProcSolu *ps= getProcSolu();
    assert(ps); 
    return ps->getDomainPtr();
  }

//! @brief Return a pointer to the integrator.
XC::Integrator *XC::ProcSoluControl::getIntegratorPtr(void)
  {
    ProcSolu *ps= getProcSolu();
    assert(ps);
    return ps->getIntegratorPtr();
  }

//! @brief Return a const pointer to the integrator.
const XC::Integrator *XC::ProcSoluControl::getIntegratorPtr(void) const
  {
    const ProcSolu *ps= getProcSolu();
    assert(ps);
    return ps->getIntegratorPtr();
  }

//! @bried Return a reference to the model wrapper container.
XC::MapModelWrapper &XC::ProcSoluControl::getModelWrapperContainer(void)
  { return solu_models; }

//! @bried Return a reference to the solution procedures container.
XC::AnalysisAggregationMap &XC::ProcSoluControl::getAnalysisAggregationContainer(void)
  { return solu_methods; }

//! @brief Return a pointer to the model wrapper with the identifier
//! being passed as parameter.
const XC::ModelWrapper *XC::ProcSoluControl::getModelWrapper(const std::string &cod) const
  { return solu_models.getModelWrapper(cod); }

//! @brief Return a pointer to the model wrapper with the identifier
//! passed as parameter.
XC::ModelWrapper *XC::ProcSoluControl::getModelWrapper(const std::string &cod)
  { return solu_models.getModelWrapper(cod); }

//! @brief Return a const pointer to the solution method.
const XC::AnalysisAggregation *XC::ProcSoluControl::getAnalysisAggregation(const std::string &cod) const
  { return solu_methods.getAnalysisAggregation(cod); }

//! @brief Return a const pointer to the solution method.
XC::AnalysisAggregation *XC::ProcSoluControl::getAnalysisAggregation(const std::string &cod)
  { return solu_methods.getAnalysisAggregation(cod); }

//! @brief Revert to the initial state.
void XC::ProcSoluControl::revertToStart(void)
  {
    getDomain()->revertToStart();
    solu_methods.revertToStart();
  }

//! @brief Clear all.
void XC::ProcSoluControl::clearAll(void)
  {
    solu_models.clearAll();
    solu_methods.clearAll();
  }

