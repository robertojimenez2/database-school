from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, func
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
import os


# 1. CONFIGURACIÓN DE LA BASE DE DATOS
# ==========================================
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./finalbd.db")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 2. MODELOS SQLALCHEMY (Mapeo de tus Tablas)
# ==========================================
class Carrera(Base):
    __tablename__ = "Carrera"
    clave_carrera = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100))

class Materia(Base):
    __tablename__ = "Materia"
    clave_materia = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100))
    creditos = Column(Integer)

class Profesor(Base):
    __tablename__ = "Profesor"
    numero_empleado = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100))
    especialidad = Column(String(100))

class Alumno(Base):
    __tablename__ = "Alumno"
    matricula_alumno = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100))
    semestre = Column(Integer)
    id_carrera = Column(Integer, ForeignKey("Carrera.clave_carrera"))
    
    # Relación para el reporte
    carrera = relationship("Carrera") 

class Calificacion(Base):
    __tablename__ = "Calificacion"
    id_calificacion = Column(Integer, primary_key=True, index=True, autoincrement=True)
    matricula_alumno = Column(Integer, ForeignKey("Alumno.matricula_alumno"))
    clave_materia = Column(Integer, ForeignKey("Materia.clave_materia"))
    calificacion = Column(Integer)

class Inscripcion(Base):
    __tablename__ = "Inscripcion"
    id_inscripcion = Column(Integer, primary_key=True, index=True, autoincrement=True)
    matricula_alumno = Column(Integer, ForeignKey("Alumno.matricula_alumno"))
    clave_materia = Column(Integer, ForeignKey("Materia.clave_materia"))
    numero_empleado = Column(Integer, ForeignKey("Profesor.numero_empleado"))
    periodo = Column(String(20))

Base.metadata.create_all(bind=engine)

# 3. ESQUEMAS PYDANTIC (Validación de Datos API)
# ==========================================
class CarreraSchema(BaseModel):
    nombre: str
    model_config = ConfigDict(from_attributes=True)

class CarreraResponse(CarreraSchema):
    clave_carrera: int

class MateriaSchema(BaseModel):
    nombre: str
    creditos: int
    model_config = ConfigDict(from_attributes=True)

class MateriaResponse(MateriaSchema):
    clave_materia: int

class ProfesorSchema(BaseModel):
    nombre: str
    especialidad: str
    model_config = ConfigDict(from_attributes=True)

class ProfesorResponse(ProfesorSchema):
    numero_empleado: int

class AlumnoSchema(BaseModel):
    nombre: str
    semestre: int
    id_carrera: int
    model_config = ConfigDict(from_attributes=True)

class AlumnoResponse(AlumnoSchema):
    matricula_alumno: int

class CalificacionSchema(BaseModel):
    matricula_alumno: int
    clave_materia: int
    calificacion: int
    model_config = ConfigDict(from_attributes=True)

class CalificacionResponse(CalificacionSchema):
    id_calificacion: int

class InscripcionSchema(BaseModel):
    matricula_alumno: int
    clave_materia: int
    numero_empleado: int
    periodo: str
    model_config = ConfigDict(from_attributes=True)

class InscripcionResponse(InscripcionSchema):
    id_inscripcion: int


# 4. APLICACIÓN FASTAPI Y ENDPOINTS CRUD
# ==========================================
app = FastAPI(title="API Universidad", description="API para gestión escolar", version="1.0.0")

# --- CRUD CARRERA ---
@app.post("/carreras/", response_model=CarreraResponse, tags=["Carrera"])
def create_carrera(item: CarreraSchema, db: Session = Depends(get_db)):
    db_item = Carrera(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/carreras/", response_model=List[CarreraResponse], tags=["Carrera"])
def read_carreras(db: Session = Depends(get_db)):
    return db.query(Carrera).all()

@app.put("/carreras/{id}", response_model=CarreraResponse, tags=["Carrera"])
def update_carrera(id: int, item: CarreraSchema, db: Session = Depends(get_db)):
    db_item = db.query(Carrera).filter(Carrera.clave_carrera == id).first()
    if not db_item: raise HTTPException(status_code=404, detail="No encontrado")
    for key, value in item.model_dump().items(): setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/carreras/{id}", tags=["Carrera"])
def delete_carrera(id: int, db: Session = Depends(get_db)):
    db_item = db.query(Carrera).filter(Carrera.clave_carrera == id).first()
    if not db_item: raise HTTPException(status_code=404, detail="No encontrado")
    db.delete(db_item)
    db.commit()
    return {"mensaje": "Carrera eliminada"}

# --- CRUD ALUMNO ---
@app.post("/alumnos/", response_model=AlumnoResponse, tags=["Alumno"])
def create_alumno(item: AlumnoSchema, db: Session = Depends(get_db)):
    db_item = Alumno(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/alumnos/", response_model=List[AlumnoResponse], tags=["Alumno"])
def read_alumnos(db: Session = Depends(get_db)):
    return db.query(Alumno).all()

@app.put("/alumnos/{id}", response_model=AlumnoResponse, tags=["Alumno"])
def update_alumno(id: int, item: AlumnoSchema, db: Session = Depends(get_db)):
    db_item = db.query(Alumno).filter(Alumno.matricula_alumno == id).first()
    if not db_item: raise HTTPException(status_code=404, detail="No encontrado")
    for key, value in item.model_dump().items(): setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/alumnos/{id}", tags=["Alumno"])
def delete_alumno(id: int, db: Session = Depends(get_db)):
    db_item = db.query(Alumno).filter(Alumno.matricula_alumno == id).first()
    if not db_item: raise HTTPException(status_code=404, detail="No encontrado")
    db.delete(db_item)
    db.commit()
    return {"mensaje": "Alumno eliminado"}

# --- CRUD MATERIA ---
@app.post("/materias/", response_model=MateriaResponse, tags=["Materia"])
def create_materia(item: MateriaSchema, db: Session = Depends(get_db)):
    db_item = Materia(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/materias/", response_model=List[MateriaResponse], tags=["Materia"])
def read_materias(db: Session = Depends(get_db)):
    return db.query(Materia).all()

@app.put("/materias/{id}", response_model=MateriaResponse, tags=["Materia"])
def update_materia(id: int, item: MateriaSchema, db: Session = Depends(get_db)):
    db_item = db.query(Materia).filter(Materia.clave_materia == id).first()
    if not db_item: raise HTTPException(status_code=404, detail="No encontrado")
    for key, value in item.model_dump().items(): setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/materias/{id}", tags=["Materia"])
def delete_materia(id: int, db: Session = Depends(get_db)):
    db_item = db.query(Materia).filter(Materia.clave_materia == id).first()
    if not db_item: raise HTTPException(status_code=404, detail="No encontrado")
    db.delete(db_item)
    db.commit()
    return {"mensaje": "Materia eliminada"}

# --- CRUD PROFESOR ---
@app.post("/profesores/", response_model=ProfesorResponse, tags=["Profesor"])
def create_profesor(item: ProfesorSchema, db: Session = Depends(get_db)):
    db_item = Profesor(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/profesores/", response_model=List[ProfesorResponse], tags=["Profesor"])
def read_profesores(db: Session = Depends(get_db)):
    return db.query(Profesor).all()

@app.put("/profesores/{id}", response_model=ProfesorResponse, tags=["Profesor"])
def update_profesor(id: int, item: ProfesorSchema, db: Session = Depends(get_db)):
    db_item = db.query(Profesor).filter(Profesor.numero_empleado == id).first()
    if not db_item: raise HTTPException(status_code=404, detail="No encontrado")
    for key, value in item.model_dump().items(): setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/profesores/{id}", tags=["Profesor"])
def delete_profesor(id: int, db: Session = Depends(get_db)):
    db_item = db.query(Profesor).filter(Profesor.numero_empleado == id).first()
    if not db_item: raise HTTPException(status_code=404, detail="No encontrado")
    db.delete(db_item)
    db.commit()
    return {"mensaje": "Profesor eliminado"}

# --- CRUD CALIFICACION ---
@app.post("/calificaciones/", response_model=CalificacionResponse, tags=["Calificacion"])
def create_calificacion(item: CalificacionSchema, db: Session = Depends(get_db)):
    db_item = Calificacion(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/calificaciones/", response_model=List[CalificacionResponse], tags=["Calificacion"])
def read_calificaciones(db: Session = Depends(get_db)):
    return db.query(Calificacion).all()

@app.put("/calificaciones/{id}", response_model=CalificacionResponse, tags=["Calificacion"])
def update_calificacion(id: int, item: CalificacionSchema, db: Session = Depends(get_db)):
    db_item = db.query(Calificacion).filter(Calificacion.id_calificacion == id).first()
    if not db_item: raise HTTPException(status_code=404, detail="No encontrado")
    for key, value in item.model_dump().items(): setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/calificaciones/{id}", tags=["Calificacion"])
def delete_calificacion(id: int, db: Session = Depends(get_db)):
    db_item = db.query(Calificacion).filter(Calificacion.id_calificacion == id).first()
    if not db_item: raise HTTPException(status_code=404, detail="No encontrado")
    db.delete(db_item)
    db.commit()
    return {"mensaje": "Calificacion eliminada"}

# --- CRUD INSCRIPCION ---
@app.post("/inscripciones/", response_model=InscripcionResponse, tags=["Inscripcion"])
def create_inscripcion(item: InscripcionSchema, db: Session = Depends(get_db)):
    db_item = Inscripcion(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/inscripciones/", response_model=List[InscripcionResponse], tags=["Inscripcion"])
def read_inscripciones(db: Session = Depends(get_db)):
    return db.query(Inscripcion).all()

@app.put("/inscripciones/{id}", response_model=InscripcionResponse, tags=["Inscripcion"])
def update_inscripcion(id: int, item: InscripcionSchema, db: Session = Depends(get_db)):
    db_item = db.query(Inscripcion).filter(Inscripcion.id_inscripcion == id).first()
    if not db_item: raise HTTPException(status_code=404, detail="No encontrado")
    for key, value in item.model_dump().items(): setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/inscripciones/{id}", tags=["Inscripcion"])
def delete_inscripcion(id: int, db: Session = Depends(get_db)):
    db_item = db.query(Inscripcion).filter(Inscripcion.id_inscripcion == id).first()
    if not db_item: raise HTTPException(status_code=404, detail="No encontrado")
    db.delete(db_item)
    db.commit()
    return {"mensaje": "Inscripcion eliminada"}

# ==========================================
# 5. ENDPOINTS DE REPORTES 
# ==========================================
@app.get("/reportes/promedio-alumnos", tags=["Reportes"])
def reporte_promedio_alumnos(db: Session = Depends(get_db)):
    """Genera un reporte con el promedio de calificaciones por alumno (incluye los que no tienen calificaciones)."""
    resultados = db.query(
        Alumno.nombre,
        func.avg(Calificacion.calificacion).label('promedio')
    ).outerjoin(Calificacion, Alumno.matricula_alumno == Calificacion.matricula_alumno)\
     .group_by(Alumno.matricula_alumno).all()
    
    return [{"alumno": r.nombre, "promedio": round(r.promedio, 2) if r.promedio else 0} for r in resultados]

@app.get("/reportes/alumnos-por-carrera", tags=["Reportes"])
def reporte_alumnos_carrera(db: Session = Depends(get_db)):
    """Genera un reporte del total de alumnos inscritos en cada carrera."""
    resultados = db.query(
        Carrera.nombre,
        func.count(Alumno.matricula_alumno).label('total_alumnos')
    ).outerjoin(Alumno, Carrera.clave_carrera == Alumno.id_carrera)\
     .group_by(Carrera.clave_carrera).all()
    
    return [{"carrera": r.nombre, "total_alumnos": r.total_alumnos} for r in resultados]

# ==========================================
# 6. INTERFAZ GRAFICA SENCILLA 
# ==========================================
@app.get("/", tags=["Frontend"])
def get_frontend():
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Panel de Administración - Universidad</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; color: #333; margin: 0; padding: 20px; }
            h1, h3 { color: #2c3e50; text-align: center; }
            .container { max-width: 1000px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            
            .btn-azul { background-color: #3498db; color: white; border: none; padding: 10px 15px; border-radius: 5px; cursor: pointer; font-size: 14px; margin: 5px; }
            .btn-azul:hover { background-color: #2980b9; }
            .btn-verde { background-color: #27ae60; color: white; border: none; padding: 10px 15px; border-radius: 5px; cursor: pointer; font-size: 14px; margin: 5px; }
            .btn-verde:hover { background-color: #2ecc71; }
            
            .btn-editar { background-color: #f39c12; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer; font-size: 12px; margin-right: 5px; }
            .btn-eliminar { background-color: #e74c3c; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer; font-size: 12px; }
            .btn-nuevo { background-color: #8e44ad; color: white; border: none; padding: 10px 15px; border-radius: 5px; cursor: pointer; font-size: 14px; margin-bottom: 10px; display: none; }
            
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
            th { background-color: #f8f9fa; font-weight: bold; }
            .separador { border: 0; height: 1px; background: #eee; margin: 20px 0; }
            
            #modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); justify-content: center; align-items: center; }
            .modal-content { background: white; padding: 20px; border-radius: 8px; width: 400px; box-shadow: 0 4px 6px rgba(0,0,0,0.2); }
            .modal-content h2 { margin-top: 0; color: #2c3e50; }
            .form-group { margin-bottom: 15px; }
            .form-group label { display: block; font-weight: bold; margin-bottom: 5px; text-transform: capitalize; }
            .form-group input { width: 100%; padding: 8px; box-sizing: border-box; border: 1px solid #ccc; border-radius: 4px; }
            .modal-actions { text-align: right; margin-top: 20px; }
            .btn-cancelar { background-color: #95a5a6; color: white; border: none; padding: 10px 15px; border-radius: 5px; cursor: pointer; margin-right: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Sistema Escolar API</h1>
            
            <h3>Tablas  (CRUD)</h3>
            <div style="text-align: center;">
                <button class="btn-azul" onclick="seleccionarEntidad('alumnos')">Alumnos</button>
                <button class="btn-azul" onclick="seleccionarEntidad('carreras')">Carreras</button>
                <button class="btn-azul" onclick="seleccionarEntidad('materias')">Materias</button>
                <button class="btn-azul" onclick="seleccionarEntidad('profesores')">Profesores</button>
                <button class="btn-azul" onclick="seleccionarEntidad('calificaciones')">Calificaciones</button>
                <button class="btn-azul" onclick="seleccionarEntidad('inscripciones')">Inscripciones</button>
            </div>
            
            <hr class="separador">
            
            <button id="btn-nuevo" class="btn-nuevo" onclick="abrirModal()">+ Nuevo Registro</button>
            <div id="tabla-contenedor"><p style="text-align:center;">Selecciona una tabla arriba para comenzar.</p></div>

            <hr class="separador">
            
            <h3>Reportes (Solo Lectura)</h3>
            <div style="text-align: center;">
                <button class="btn-verde" onclick="cargarReporte('/reportes/promedio-alumnos')">Promedio de Alumnos</button>
                <button class="btn-verde" onclick="cargarReporte('/reportes/alumnos-por-carrera')">Alumnos por Carrera</button>
            </div>
        </div>

        <div id="modal">
            <div class="modal-content">
                <h2 id="modal-titulo">Formulario</h2>
                <form id="formulario" onsubmit="guardarRegistro(event)">
                    <div id="form-campos"></div>
                    <input type="hidden" id="id-registro">
                    <div class="modal-actions">
                        <button type="button" class="btn-cancelar" onclick="cerrarModal()">Cancelar</button>
                        <button type="submit" class="btn-verde">Guardar</button>
                    </div>
                </form>
            </div>
        </div>

        <script>

            const config = {
                'alumnos': { endpoint: '/alumnos/', pk: 'matricula_alumno', campos: ['nombre', 'semestre', 'id_carrera'] },
                'carreras': { endpoint: '/carreras/', pk: 'clave_carrera', campos: ['nombre'] },
                'materias': { endpoint: '/materias/', pk: 'clave_materia', campos: ['nombre', 'creditos'] },
                'profesores': { endpoint: '/profesores/', pk: 'numero_empleado', campos: ['nombre', 'especialidad'] },
                'calificaciones': { endpoint: '/calificaciones/', pk: 'id_calificacion', campos: ['matricula_alumno', 'clave_materia', 'calificacion'] },
                'inscripciones': { endpoint: '/inscripciones/', pk: 'id_inscripcion', campos: ['matricula_alumno', 'clave_materia', 'numero_empleado', 'periodo'] }
            };

            let entidadActual = null;
            let datosActuales = [];

            function seleccionarEntidad(entidad) {
                entidadActual = entidad;
                document.getElementById('btn-nuevo').style.display = 'inline-block';
                document.getElementById('btn-nuevo').innerText = `+ Nuevo ${entidad.toUpperCase()}`;
                cargarTabla();
            }

            async function cargarTabla() {
                const contenedor = document.getElementById('tabla-contenedor');
                contenedor.innerHTML = '<p style="text-align:center;">Cargando...</p>';
                
                try {
                    const response = await fetch(config[entidadActual].endpoint);
                    datosActuales = await response.json();
                    
                    if(datosActuales.length === 0) {
                        contenedor.innerHTML = '<p style="text-align:center;">No hay registros. Crea uno nuevo.</p>';
                        return;
                    }

                    const llaves = Object.keys(datosActuales[0]);
                    const pk = config[entidadActual].pk;

                    let html = '<table><thead><tr>';
                    llaves.forEach(llave => html += `<th>${llave.toUpperCase().replace(/_/g, ' ')}</th>`);
                    html += '<th>ACCIONES</th></tr></thead><tbody>';

                    datosActuales.forEach((fila, index) => {
                        html += '<tr>';
                        llaves.forEach(llave => html += `<td>${fila[llave]}</td>`);
                        html += `<td>
                                    <button class="btn-editar" onclick="abrirModal(${index})">Editar</button>
                                    <button class="btn-eliminar" onclick="eliminarRegistro(${fila[pk]})">Eliminar</button>
                                 </td>`;
                        html += '</tr>';
                    });
                    html += '</tbody></table>';
                    
                    contenedor.innerHTML = html;
                } catch (error) {
                    contenedor.innerHTML = `<p style="color:red; text-align:center;">Error: ${error}</p>`;
                }
            }

            function abrirModal(index = null) {
                const conf = config[entidadActual];
                const contenedorCampos = document.getElementById('form-campos');
                contenedorCampos.innerHTML = '';
                
                const esEdicion = index !== null;
                const registroEdicion = esEdicion ? datosActuales[index] : null;

                document.getElementById('modal-titulo').innerText = esEdicion ? `Editar Registro` : `Nuevo Registro`;
                document.getElementById('id-registro').value = esEdicion ? registroEdicion[conf.pk] : '';

                conf.campos.forEach(campo => {
                    const esNumero = ['id_', 'clave_', 'semestre', 'creditos', 'matricula', 'calificacion', 'numero_'].some(kw => campo.includes(kw));
                    const tipoInput = esNumero ? 'number' : 'text';
                    const valor = esEdicion ? registroEdicion[campo] : '';

                    contenedorCampos.innerHTML += `
                        <div class="form-group">
                            <label>${campo.replace(/_/g, ' ')}</label>
                            <input type="${tipoInput}" id="input-${campo}" name="${campo}" value="${valor}" required>
                        </div>
                    `;
                });

                document.getElementById('modal').style.display = 'flex';
            }

            function cerrarModal() {
                document.getElementById('modal').style.display = 'none';
            }

            async function guardarRegistro(event) {
                event.preventDefault(); // Evita que la página recargue
                
                const conf = config[entidadActual];
                const idRegistro = document.getElementById('id-registro').value;
                const metodo = idRegistro ? 'PUT' : 'POST';
                const url = idRegistro ? `${conf.endpoint}${idRegistro}` : conf.endpoint;
                
                const payload = {};
                conf.campos.forEach(campo => {
                    let valor = document.getElementById(`input-${campo}`).value;
                    if(document.getElementById(`input-${campo}`).type === 'number') {
                        valor = parseFloat(valor);
                    }
                    payload[campo] = valor;
                });

                try {
                    const response = await fetch(url, {
                        method: metodo,
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });

                    if(response.ok) {
                        cerrarModal();
                        cargarTabla(); // Recargar la tabla tras guardar
                    } else {
                        const errorMsg = await response.json();
                        alert("Error al guardar: " + JSON.stringify(errorMsg.detail));
                    }
                } catch (error) {
                    alert("Error de red: " + error);
                }
            }

            async function eliminarRegistro(id) {
                if(!confirm('¿Estás seguro de que deseas eliminar este registro?')) return;
                
                try {
                    const conf = config[entidadActual];
                    const response = await fetch(`${conf.endpoint}${id}`, {
                        method: 'DELETE'
                    });

                    if(response.ok) {
                        cargarTabla();
                    } else {
                        const errorMsg = await response.json();
                        alert("No se pudo eliminar: " + JSON.stringify(errorMsg.detail));
                    }
                } catch (error) {
                    alert("Error de red: " + error);
                }
            }

            async function cargarReporte(endpoint) {
                document.getElementById('btn-nuevo').style.display = 'none';
                entidadActual = null; // Quita el modo edición
                
                const contenedor = document.getElementById('tabla-contenedor');
                contenedor.innerHTML = '<p style="text-align:center;">Generando reporte...</p>';
                try {
                    const response = await fetch(endpoint);
                    const data = await response.json();
                    
                    if(data.length === 0) {
                        contenedor.innerHTML = '<p style="text-align:center;">No hay datos para este reporte.</p>';
                        return;
                    }

                    const llaves = Object.keys(data[0]);
                    let html = '<table><thead><tr>';
                    llaves.forEach(llave => html += `<th>${llave.toUpperCase().replace(/_/g, ' ')}</th>`);
                    html += '</tr></thead><tbody>';

                    data.forEach(fila => {
                        html += '<tr>';
                        llaves.forEach(llave => html += `<td>${fila[llave]}</td>`);
                        html += '</tr>';
                    });
                    html += '</tbody></table>';
                    
                    contenedor.innerHTML = html;
                } catch (error) {
                    contenedor.innerHTML = `<p style="color:red; text-align:center;">Error al cargar: ${error}</p>`;
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Panel de Administración - Universidad</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; color: #333; margin: 0; padding: 20px; }
            h1 { color: #2c3e50; text-align: center; }
            h3 { color: #2c3e50; text-align: center; margin-top: 5px; margin-bottom: 10px; }
            .container { max-width: 900px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            .btn-azul { background-color: #3498db; color: white; border: none; padding: 10px 15px; border-radius: 5px; cursor: pointer; font-size: 14px; margin: 5px; }
            .btn-azul:hover { background-color: #2980b9; }
            .btn-verde { background-color: #27ae60; color: white; border: none; padding: 10px 15px; border-radius: 5px; cursor: pointer; font-size: 14px; margin: 5px; }
            .btn-verde:hover { background-color: #2ecc71; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
            th { background-color: #f8f9fa; font-weight: bold; }
            .swagger-link { display: block; text-align: center; margin-top: 30px; color: #e74c3c; text-decoration: none; font-weight: bold; }
            .separador { border: 0; height: 1px; background: #eee; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1> Sistema Escolar API</h1>
            
            <h3>Tablas </h3>
            <div style="text-align: center;">
                <button class="btn-azul" onclick="cargarDatos('/alumnos/')">Ver Alumnos</button>
                <button class="btn-azul" onclick="cargarDatos('/carreras/')">Ver Carreras</button>
                <button class="btn-azul" onclick="cargarDatos('/materias/')">Ver Materias</button>
                <button class="btn-azul" onclick="cargarDatos('/profesores/')">Ver Profesores</button>
            </div>
            
            <hr class="separador">
            
            <h3> Apartado de Reportes</h3>
            <div style="text-align: center;">
                <button class="btn-verde" onclick="cargarDatos('/reportes/promedio-alumnos')">Promedio de Todos los Alumnos</button>
                <button class="btn-verde" onclick="cargarDatos('/reportes/alumnos-por-carrera')">Total de Alumnos por Carrera</button>
            </div>
            
            <div id="tabla-contenedor"></div>

            <a href="/docs" class="swagger-link" target="_blank">Abrir documentacion de FastAPI</a>
        </div>

        <script>
            async function cargarDatos(endpoint) {
                const contenedor = document.getElementById('tabla-contenedor');
                contenedor.innerHTML = '<p style="text-align:center; margin-top:20px;">Cargando datos...</p>';
                try {
                    const response = await fetch(endpoint);
                    const data = await response.json();
                    
                    if(data.length === 0) {
                        contenedor.innerHTML = '<p style="text-align:center; margin-top:20px;">No hay registros para mostrar aún.</p>';
                        return;
                    }

                    const llaves = Object.keys(data[0]);
                    let html = '<table><thead><tr>';
                    llaves.forEach(llave => html += `<th>${llave.toUpperCase().replace(/_/g, ' ')}</th>`);
                    html += '</tr></thead><tbody>';

                    data.forEach(fila => {
                        html += '<tr>';
                        llaves.forEach(llave => html += `<td>${fila[llave]}</td>`);
                        html += '</tr>';
                    });
                    html += '</tbody></table>';
                    
                    contenedor.innerHTML = html;
                } catch (error) {
                    contenedor.innerHTML = `<p style="color:red; text-align:center; margin-top:20px;">Error al cargar los datos: ${error}</p>`;
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Panel de Administración - Universidad</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; color: #333; margin: 0; padding: 20px; }
            h1 { color: #2c3e50; text-align: center; }
            .container { max-width: 900px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            button { background-color: #3498db; color: white; border: none; padding: 10px 15px; border-radius: 5px; cursor: pointer; font-size: 14px; margin: 5px; }
            button:hover { background-color: #2980b9; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
            th { background-color: #f8f9fa; font-weight: bold; }
            .swagger-link { display: block; text-align: center; margin-top: 20px; color: #e74c3c; text-decoration: none; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎓 Sistema Escolar API</h1>
            <div style="text-align: center;">
                <button onclick="cargarDatos('/alumnos/')">Ver Alumnos</button>
                <button onclick="cargarDatos('/carreras/')">Ver Carreras</button>
                <button onclick="cargarDatos('/reportes/promedio-alumnos')">Reporte: Promedios</button>
            </div>
            
            <div id="tabla-contenedor"></div>

            <a href="/docs" class="swagger-link" target="_blank">Abrir Documentación</a>
        </div>

        <script>
            async function cargarDatos(endpoint) {
                const contenedor = document.getElementById('tabla-contenedor');
                contenedor.innerHTML = '<p style="text-align:center;">Cargando datos...</p>';
                try {
                    const response = await fetch(endpoint);
                    const data = await response.json();
                    
                    if(data.length === 0) {
                        contenedor.innerHTML = '<p style="text-align:center;">No hay registros en esta tabla aún.</p>';
                        return;
                    }

                    const llaves = Object.keys(data[0]);
                    let html = '<table><thead><tr>';
                    llaves.forEach(llave => html += `<th>${llave.toUpperCase().replace('_', ' ')}</th>`);
                    html += '</tr></thead><tbody>';

                    data.forEach(fila => {
                        html += '<tr>';
                        llaves.forEach(llave => html += `<td>${fila[llave]}</td>`);
                        html += '</tr>';
                    });
                    html += '</tbody></table>';
                    
                    contenedor.innerHTML = html;
                } catch (error) {
                    contenedor.innerHTML = `<p style="color:red; text-align:center;">Error al cargar: ${error}</p>`;
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)