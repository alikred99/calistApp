let horaInicio
let horaFin
let contador = 0
let intervalo
let sesionId
document.getElementById("btn-fin-entreno").disabled = true
document.getElementById("btn-inicio-entreno").addEventListener("click", function(){
    horaInicio = new Date()
    intervalo = setInterval(function(){
        contador += 1
        document.getElementById("timer").textContent = contador
    }, 1000)
    document.getElementById("btn-inicio-entreno").disabled = true
    document.getElementById("btn-fin-entreno").disabled = false
    horaInicioFormateada = horaInicio.toTimeString().slice(0,8)
    fetch("http://localhost:8000/sesiones", {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify({
        hora_inicio : horaInicioFormateada
    })
})
    .then(response => response.json())
    .then(data => {
        sesionId = data.id
        console.log(sesionId)
    })

})

document.getElementById("btn-fin-entreno").addEventListener("click", function(){
    horaFin = new Date()
    document.getElementById("btn-fin-entreno").disabled = true
    document.getElementById("btn-inicio-entreno").disabled = false
    clearInterval(intervalo)
    contador = 0
    document.getElementById("timer").textContent = contador
    horaFinFormateada = horaFin.toTimeString().slice(0,8)
    
    fetch(`http://localhost:8000/sesiones/${sesionId}`, {
    method: "PUT",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify({
        hora_fin : horaFinFormateada
    })
})
    .then(response => response.json())
    .then(data => console.log(data))

})

function cargarCatalogo() {
    fetch ("http://localhost:8000/catalogo")
    .then(response => response.json())
    .then(data => {
        const select = document.getElementById("catalogo-select")

        data.forEach(ejercicio => {
            const item = document.createElement("option")
            item.textContent = ejercicio.nombre
            item.value = ejercicio.id
            select.appendChild(item)
        });
    })
}

document.getElementById("btn-agregar-ejercicio").addEventListener("click", function(){
    const select = document.getElementById("catalogo-select")
    const nombre = select.selectedOptions[0].text
    const reps = document.getElementById("catalogo-reps").value
    const series = document.getElementById("catalogo-series").value
    fetch(`http://localhost:8000/ejercicios/${sesionId}`, {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify({
        nombre: nombre,
        reps: reps,
        series: series
    })
}) 
    .then(response => response.json())
    .then(data => cargarEjercicios())
    
})


function cargarEjercicios(){
    fetch(`http://localhost:8000/ejercicios/sesion/${sesionId}`)
    .then(response => response.json())
    .then(data => {
        const historial = document.getElementById("historial-ejercicios")
        historial.innerHTML = ""
        data.forEach(ejercicio => {
            const item = document.createElement("p")
            item.textContent = `${ejercicio.nombre} - ${ejercicio.reps} reps x ${ejercicio.series} series`
            historial.appendChild(item)
        });
        
    })
}

document.getElementById("btn-mostrar-historial").addEventListener("click", function(){
    fetch("http://localhost:8000/sesiones/historial")
    .then(response => response.json())
    .then(data => {
        const historial = document.getElementById("historial-sesiones")
        historial.innerHTML = ""
        data.forEach(sesion => {
            const item = document.createElement("p")
            let textoEjercicios = ""
            sesion.ejercicios.forEach(ejercicio => {
                textoEjercicios += `${ejercicio.nombre} (${ejercicio.reps}x${ejercicio.series}) `
                
            })
            item.textContent = `Fecha: ${sesion.fecha} | ${sesion.hora_inicio} - ${sesion.hora_fin} | Ejercicios: ${textoEjercicios} | Duración: ${sesion.duracion}`
            historial.appendChild(item)
        });
        
    })
})

cargarCatalogo()