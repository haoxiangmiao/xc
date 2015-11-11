//----------------------------------------------------------------------------
//  programa XC; cálculo mediante el método de los elementos finitos orientado
//  a la solución de problemas estructurales.
//
//  Copyright (C)  Luis Claudio Pérez Tato
//
//  El programa deriva del denominado OpenSees <http://opensees.berkeley.edu>
//  desarrollado por el «Pacific earthquake engineering research center».
//
//  Salvo las restricciones que puedan derivarse del copyright del
//  programa original (ver archivo copyright_opensees.txt) este
//  software es libre: usted puede redistribuirlo y/o modificarlo 
//  bajo los términos de la Licencia Pública General GNU publicada 
//  por la Fundación para el Software Libre, ya sea la versión 3 
//  de la Licencia, o (a su elección) cualquier versión posterior.
//
//  Este software se distribuye con la esperanza de que sea útil, pero 
//  SIN GARANTÍA ALGUNA; ni siquiera la garantía implícita
//  MERCANTIL o de APTITUD PARA UN PROPÓSITO DETERMINADO. 
//  Consulte los detalles de la Licencia Pública General GNU para obtener 
//  una información más detallada. 
//
// Debería haber recibido una copia de la Licencia Pública General GNU 
// junto a este programa. 
// En caso contrario, consulte <http://www.gnu.org/licenses/>.
//----------------------------------------------------------------------------
//Block.cc

#include "Block.h"
#include "Pnt.h"
#include "SupCuadrilatera.h"
#include "xc_basic/src/matrices/m_int.h"
#include "xc_utils/src/geom/d3/BND3d.h"
#include "xc_utils/src/base/CmdStatus.h"
#include "Face.h"
#include "xc_utils/src/base/any_const_ptr.h"
#include "domain/mesh/node/Node.h"
#include "domain/mesh/element/Element.h"
#include "med.h"
#include "preprocessor/Preprocessor.h"
#include "preprocessor/set_mgmt/Set.h"
#include "xc_utils/src/geom/pos_vec/MatrizPos3d.h"
#include "xc_utils/src/geom/pos_vec/TritrizPos3d.h"
#include "vtkCellType.h"

// Numeración de los vértices:
//
//       5        8
//       +--------+
//      /        /|
//     /      7 / |
//  6 +--------+  |
//    |        |  |
//    |        |  + 4
//    |        | /
//    |        |/
//    +--------+
//    2        3
//
// Numeración de las caras:
//
//                
//       +--------+         0: Base; vértices 1,2,3,4.
//      /   5    /|         1: Lateral izquierdo; vértices 1,2,6,5.
//     /        / |         2: Cara frontal; vértices 2,3,7,6.
//    +--------+  |         3: Lateral derecho; vértices 3,4,8,7.
//    |        | 3|         4: Cara dorsal; vértices 1,4,8,5.
//    |        |  +         5: Tapa; vértices 5,6,7,8.
//    |   2    | /
//    |        |/
//    +--------+
//

//! @brief Constructor.
XC::Block::Block(Preprocessor *m,const std::string &nombre)
  : Body(m,nombre) {}

//! @brief Constructor virtual.
XC::SetEstruct *XC::Block::getCopy(void) const
  { return new Block(*this); }


//! @brief Lee un objeto Block desde el archivo de entrada.
//!
//! Soporta los comandos:
//!
//! - superficie: Lee la superficie que limita al sólido.
bool XC::Block::procesa_comando(CmdStatus &status)
  {
    const std::string cmd= deref_cmd(status.Cmd());
    if(verborrea>2)
      std::clog << "(Block) Procesando comando: " << cmd << std::endl;

    if(cmd == "set_cara")
      {
        const size_t id_cara= interpretaSize_t(status.GetString());
        inserta(id_cara);
        return true;
      }
    if(cmd == "def_caras")
      {
        const std::vector<size_t> claves= crea_vector_size_t(status.GetString());
        for(std::vector<size_t>::const_iterator i= claves.begin();i!=claves.end();i++)
          inserta(*i);
        return true;
      }
    else
      return Body::procesa_comando(status);
  }

//! @brief Interfaz con VTK.
int XC::Block::getVtkCellType(void) const
  { return VTK_HEXAHEDRON; }

//! @brief Interfaz con el formato MED de Salome.
int XC::Block::getMEDCellType(void) const
  { return MED_HEXA8; }

//! @brief Comprueba que los números de divisiones de las líneas son compatibles.
bool XC::Block::checkNDivs(void) const
  {
    return (sups[0].checkNDivs() && sups[1].checkNDivs() && sups[2].checkNDivs() && sups[3].checkNDivs() && sups[4].checkNDivs() && sups[5].checkNDivs());
  }

//! @brief Devuelve el número de líneas del objeto.
size_t XC::Block::NumLineas(void) const
  { return 12; }

//! @brief Devuelve el número de vértices del objeto.
size_t XC::Block::NumVertices(void) const
  { return 8; }

//! @brief Devuelve el número de vértices del objeto.
size_t XC::Block::NumCaras(void) const
  { return 6; }

//! @brief Devuelve la cara del sólido cuyo índice se pasa como parámetro.
const XC::Block::Cara *XC::Block::GetCara(const size_t &i) const
  { return &sups[i-1]; }

//! @brief Devuelve la cara del sólido cuyo índice se pasa como parámetro.
XC::Block::Cara *XC::Block::GetCara(const size_t &i)
  { return &sups[i-1]; }

//! @brief Devuelve la arista del sólido cuyo índice se pasa como parámetro.
const XC::CmbEdge::Lado *XC::Block::GetArista(const size_t &i) const
  {
    const CmbEdge::Lado *retval(nullptr);
    switch(i)
      {
        case 1:
        case 2:
        case 3:
        case 4:
          retval=sups[0].GetLado(i);
          break;
        case 5:
        case 6:
        case 7:
        case 8:
          retval= sups[i-4].GetLado(4);
          break;
        case 9:
        case 10:
        case 11:
        case 12:
          retval= sups[5].GetLado(i-8);
          break;
        default:
          retval= nullptr;
          break;
      }
    return retval;
  }

//! @brief Devuelve el vértice del sólido cuyo índice se pasa como parámetro.
const XC::Pnt *XC::Block::GetVertice(const size_t &i) const
  {
    if(i<=4)
      return sups[0].GetVertice(i);
    else if(i<=8)
      return sups[5].GetVertice(i-4);
    else
      return nullptr;
  }

//! @brief Devuelve el vértice del sólido cuyo índice se pasa como parámetro.
XC::Pnt *XC::Block::GetVertice(const size_t &i)
  {
    if(i<=4)
      return sups[0].GetVertice(i);
    else if(i<=8)
      return sups[5].GetVertice(i-4);
    else
      return nullptr;
  }

//! @brief Devuelve las superficies que limitan el sólido.
std::set<const XC::Face *> XC::Block::GetSuperficies(void)
  {
    std::set<const Face *> retval;
    if(!sups[0].Vacia()) retval.insert(sups[0].Superficie());
    if(!sups[1].Vacia()) retval.insert(sups[1].Superficie());
    if(!sups[2].Vacia()) retval.insert(sups[2].Superficie());
    if(!sups[3].Vacia()) retval.insert(sups[3].Superficie());
    if(!sups[4].Vacia()) retval.insert(sups[4].Superficie());
    if(!sups[5].Vacia()) retval.insert(sups[5].Superficie());
    return retval;
  }

//! @brief Actualiza la topología de las superficies que limitan el sólido.
void XC::Block::actualiza_topologia(void)
  {
    if(!sups[0].Vacia()) set_surf(sups[0].Superficie());
    if(!sups[1].Vacia()) set_surf(sups[1].Superficie());
    if(!sups[2].Vacia()) set_surf(sups[2].Superficie());
    if(!sups[3].Vacia()) set_surf(sups[3].Superficie());
    if(!sups[4].Vacia()) set_surf(sups[4].Superficie());
    if(!sups[5].Vacia()) set_surf(sups[5].Superficie());
  }

//! Devuelve el índice que corresponde a la superficie que se pasa como
//! parámetro de acuerdo con el siguiente criterio:
//! - Si la superficie es la primera que define el sólido, entonces es
//!  la base.
//! - Si ya hay alguna superficie definida entonces buscamos el índice
//!  en la base de la línea común de está última con la que se pasa como
//!  parámetro. Si tal línea existe, dicho índice es el que corresponde
//!  a la superficie en el sólido.
size_t XC::Block::indice(Face *s) const
  {
    size_t retval= 0;
    if(sups[0].Vacia())
      retval= 0; //Es la base.
    else //La base ya está asignada.
      {
        const Face *base= sups[0].Superficie();
        size_t primero= base->BordeComun(*s); //Linea comun de "s" con la base.
        if(primero)
          retval= primero; //Es un lateral.
        else
          retval= 5; //Es la tapa.
      }
    return retval;
  }

//! @brief Establece como límite del sólido la superficie que se pasa como parámetro.
void XC::Block::coloca(const size_t &i,Face *s)
  {
    size_t primero= 1;
    int sentido= 1;
    if( (i>0) && (i<5)) //Es un lateral
      {
        const Face *base= sups[0].Superficie();
        primero= s->BordeComun(*base); //Indice de la línea común de s con la base.
        const Edge *linea= base->GetLado(i)->Borde();
        sentido= base->SentidoBorde(linea,*s);
      }
    if(i == 5) //Es la tapa
      {
        //Buscamos una cara asignada.
        size_t icara= 1;
        Face *cara= sups[1].Superficie();
        if(!cara) { icara=2; cara= sups[icara].Superficie(); }
        if(!cara) { icara=3; cara= sups[icara].Superficie(); }
        if(!cara) { icara=4; cara= sups[icara].Superficie(); }
        if(!cara)
          std::cerr << "Error: Block; antes de introducir la cara 5 hay que introducir la 1 o la 2 o la 3 o la 4." << std::endl;
        else
          {
            primero= cara->BordeComun(*s); //Indice de la línea común de s con la cara.
            if(primero) //Tienen lado común.
              {
                const Edge *linea= cara->GetLado(primero)->Borde();
                sentido= -cara->SentidoBorde(linea,*s);
              }
            else //No tienen lado común.
              {
                std::cerr << "Error: Block(" << GetNombre() << "); la cara " << s->GetNombre() 
                          << " no tiene lado común con la cara " << cara->GetNombre() << '.' << std::endl;
              }
          }
      }
    bool directo= true;
    if(sentido==1)
      directo= true;
    else
      if(sentido==-1)
        directo= false;
      else
        std::cerr << "Las superficies no tienen borde común." << std::endl;
    sups[i]= Cara(s,primero,directo);
  }

//! @brief Inserta la superficie cuyo identificador se pasa como parámetro (si la encuentra).
void XC::Block::inserta(const size_t &i)
  {
    Face *s= BuscaFace(i);
    if(s)
      coloca(indice(s),s);
    else
      std::cerr << "Block::inserta; No se encontró la superficie: " << i << std::endl;
  }

//! @brief Crea e inserta las caras partir de los índices que se pasan
//! como parámetro.
void XC::Block::add_caras(const std::vector<size_t> &indices_caras)
  {
    const size_t nc= indices_caras.size(); //No. de índices leídos.
    for(size_t i= 0;i<nc;i++)
      inserta(indices_caras[i]);
  }

//! @brief Lanza la creación de nodos de las caras.
void XC::Block::crea_nodos_caras(void)
  {
    sups[0].crea_nodos();
    sups[1].crea_nodos();
    sups[2].crea_nodos();
    sups[3].crea_nodos();
    sups[4].crea_nodos();
    sups[5].crea_nodos();
  }

//! @brief Devuelve (ndivI+1)*(ndivJ+1)*(ndivK+1) posiciones para los nodos.
//!
//! La "tritriz" de puntos devuelta esta organizada de la siguiente manera.
//! - El punto de índices (0,1,1) (capa,fila,col) coincide con el vértice 1.
//! - El índice de capa avanza desde 0 para la cara 1 hasta ncapas para la cara 6.
//! - El índice de fila avanza desde 1 para la cara 5 hasta nfilas para la cara 3.
//! - El índice de columna avanza desde 1 para la cara 2 hasta ncol para la cara 4.
//!
//! En consecuencia:
//! - La arista 1 tiene indices (0,j=1..nfil,1) 
//! - La arista 2 tiene indices (0,nfil,k=1..ncol) 
//! - La arista 3 tiene indices (0,j=1..nfil,ncol)
//! - La arista 4 tiene indices (0,1,k=1..ncol)

//! - La arista 5 tiene indices (i=0..ncapas,1,1) 
//! - La arista 6 tiene indices (i=0..ncapas,nfil,1) 
//! - La arista 7 tiene indices (i=0..ncapas,nfil,ncol) 
//! - La arista 8 tiene indices (i=0..ncapas,1,ncol) 

//! - La arista 9 tiene indices (ncapas,j=1..nfil,1) 
//! - La arista 10 tiene indices (ncapas,nfil,k=1..ncol) 
//! - La arista 11 tiene indices (ncapas,j=1..nfil,ncol) 
//! - La arista 12 tiene indices (ncapas,1,k=1..ncol) 
TritrizPos3d XC::Block::get_posiciones(void) const
  {
    const size_t ndiv_12= NDivI();
    const size_t ndiv_23= NDivJ();
    const size_t ndiv_15= NDivK();
    const Pos3d p1= GetVertice(1)->GetPos();
    const Pos3d p2= GetVertice(2)->GetPos();
    const Pos3d p3= GetVertice(3)->GetPos();
    const Pos3d p4= GetVertice(4)->GetPos();
    const Pos3d p5= GetVertice(5)->GetPos();
    const Pos3d p6= GetVertice(6)->GetPos();
    const Pos3d p7= GetVertice(7)->GetPos();
    const Pos3d p8= GetVertice(8)->GetPos();
    const MatrizPos3d ptos_l5= MatrizPos3d(p1,p5,ndiv_15);
    const MatrizPos3d ptos_l6= MatrizPos3d(p2,p6,ndiv_15);
    const MatrizPos3d ptos_l7= MatrizPos3d(p3,p7,ndiv_15);
    const MatrizPos3d ptos_l8= MatrizPos3d(p4,p8,ndiv_15);
    TritrizPos3d retval(ptos_l5,ptos_l6,ptos_l7,ptos_l8,ndiv_12,ndiv_23);
    return retval;
  }

//! @brief Devuelve el número de divisiones según la arista 1->2.
size_t XC::Block::NDivI(void) const
  { return GetArista(1)->NDiv(); }

//! @brief Devuelve el número de divisiones según la arista 2->3.
size_t XC::Block::NDivJ(void) const
  { return GetArista(2)->NDiv(); }

//! @brief Devuelve el número de divisiones según la arista 1->5.
size_t XC::Block::NDivK(void) const
  { return GetArista(5)->NDiv(); }

//! @brief Crea los nodos del bloque.
void XC::Block::crea_nodos(void)
  {
    std::cout << "Entra Block::crea_nodos" << std::endl;
    checkNDivs();
    if(nodos.Null())
      {
        crea_nodos_caras();
        Cara &base= sups[0];
        Cara &tapa= sups[5];
        Cara &latIzdo= sups[1];
        Cara &latDcho= sups[3];
        Cara &caraFrontal= sups[2];
        Cara &caraDorsal= sups[4];

        const size_t capas= NDivK()+1;
        const size_t filas= NDivJ()+1;
        const size_t cols= NDivI()+1;
        nodos = TritrizPtrNod(capas,filas,cols); //Punteros a nodo.
        TritrizPos3d pos_nodos= get_posiciones(); //Posiciones de los nodos.

        //Vértices.
	nodos(1,1,1)= GetVertice(1)->GetNodo();
        nodos(1,filas,1)= GetVertice(2)->GetNodo();
	nodos(1,filas,cols)= GetVertice(3)->GetNodo();
        nodos(1,1,cols)= GetVertice(4)->GetNodo();
	nodos(capas,1,1)= GetVertice(5)->GetNodo();
        nodos(capas,filas,1)= GetVertice(6)->GetNodo();
	nodos(capas,filas,cols)= GetVertice(7)->GetNodo();
        nodos(capas,1,cols)= GetVertice(8)->GetNodo();

        const Node *n1= nodos(1,1,1);
        const Node *n2= nodos(1,filas,1);
        const Node *n3= nodos(1,filas,cols);
        const Node *n4= nodos(1,1,cols);
        const Node *n5= nodos(capas,1,1);
        const Node *n6= nodos(capas,filas,1);
        const Node *n7= nodos(capas,filas,cols);
        const Node *n8= nodos(capas,1,cols);

    std::cout << "capas= " << capas << std::endl;
    std::cout << "filas= " << filas << std::endl;
    std::cout << "cols= " << cols << std::endl;

    std::cout << "base" << std::endl;
        //Enlazamos con los nodos de la base i=1
        ID IJK1= base.Superficie()->getNodeIndices(n1);
        ID IJK2= base.Superficie()->getNodeIndices(n2);
        ID IJK4= base.Superficie()->getNodeIndices(n4);
        size_t ind_i= 0, ind_j= 0;
        if((IJK2[1]-IJK1[1])>0)
          { ind_i= 1; ind_j= 2; }
        else if((IJK2[2]-IJK1[2])>0)
          { ind_j= 1; ind_i= 2; }
        const size_t nf= abs(IJK2[ind_i]-IJK1[ind_i])+1;
        const size_t nc= abs(IJK4[ind_j]-IJK1[ind_j])+1;
	std::cout << "IJK1= " << IJK1 << std::endl;
	std::cout << "IJK2= " << IJK2 << std::endl;
	std::cout << "IJK4= " << IJK4 << std::endl;
	std::cout << "ind_i= " << ind_i << " nf= " << nf << std::endl;
	std::cout << "ind_j= " << ind_j << " nc= " << nc << std::endl;
        double d2= 0;
        for(size_t i=1;i<=nf;i++)
          for(size_t j=1;j<=nc;j++)
            {
              size_t J= (IJK2[ind_i]-IJK1[ind_i])/(nf-1)*(i-1)+IJK1[ind_i];
              size_t K= (IJK4[ind_j]-IJK1[ind_j])/(nc-1)*(j-1)+IJK1[ind_j];
              if(ind_i<ind_j)
                nodos(1,J,K)= base.GetNodo(i,j);
              else
                nodos(1,J,K)= base.GetNodo(j,i);
              d2= dist2(nodos(1,J,K)->getPosInicial3d(),pos_nodos(1,J,K));
              if(d2>1e-4)
		std::cerr << "Block::crea_nodos; error al enlazar el nodo: ("
                          << i << "," << j << ") de la base." << std::endl;
	      std::cout << "i= " << i << " j= " << j << " J= " << J << " K= " << K 
                        << " dist2= " << d2 << std::endl;
            }
	/*
    std::cout << "tapa" << std::endl;
        //Tapa i=capas
        IJK1= tapa.Superficie()->getNodeIndices(n5);
        IJK2= tapa.Superficie()->getNodeIndices(n7);
        for(size_t i=1;i<=filas;i++)
          for(size_t j=1;j<=cols;j++)
            {
              size_t J= (IJK2[1]-IJK1[1])/(filas-1)*(i-1)+IJK1[1];
              size_t K= (IJK2[2]-IJK1[2])/(cols-1)*(j-1)+IJK1[2];
              nodos(capas,J,K)= tapa.GetNodo(i,j);
            }

        //Lateral izquierdo j=1.
        IJK1= latIzdo.Superficie()->getNodeIndices(n1);
        IJK2= latIzdo.Superficie()->getNodeIndices(n6);
        for(size_t i=1;i<=filas;i++)
          for(size_t j=1;j<=cols;j++)
            {
              size_t J= (IJK2[1]-IJK1[1])/(filas-1)*(j-1)+IJK1[1];
              size_t K= (IJK2[2]-IJK1[2])/(filas-1)*(j-1)+IJK1[2];
              nodos(capas,J,K)= tapa.GetNodo(i,j);
            }
	*/

        for(size_t k= 2;k<capas;k++) //Capas interiores.
          for(size_t j= 2;j<filas;j++) //Filas interiores.
            for(size_t i= 2;i<cols;i++) //Columnas interiores.
              crea_nodo(pos_nodos(i,j,k),i,j,k);
      }
    else
      if(verborrea>2)
        std::clog << "Block::crea_nodos; los nodos de la entidad: '" << GetNombre() << "' ya existen." << std::endl;      
  }

//! @brief Crea la malla de elementos finitos interior al bloque.
void XC::Block::Malla(dir_mallado dm)
  {
    if(verborrea>3)
      std::clog << "Mallando Block...(" << GetNombre() << ")...";
    crea_nodos();
    if(elementos.Null())
      crea_elementos(dm);
    else
      if(verborrea>2)
        std::clog << "Block::Malla; los nodos de la entidad: '" << GetNombre() << "' ya existen." << std::endl;      
    if(verborrea>3)
      std::clog << "hecho." << std::endl;
  }

//! Devuelve la propiedad del objeto cuyo código se pasa
//! como parámetro.
//!
//! Soporta las propiedades:
//! -dim: Devuelve la dimensión del objeto.
any_const_ptr XC::Block::GetProp(const std::string &cod) const
  {
    return Body::GetProp(cod);
  }
