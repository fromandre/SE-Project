//raccogli stelle
const uno = document.getElementById("uno")
const due = document.getElementById("due")
const tre = document.getElementById("tre")
const quattro = document.getElementById("quattro")
const cinque = document.getElementById("cinque")
const form = document.querySelector('.rate-form')
const conferma = document.getElementById('conferma')
const csrf = document.getElementsByName('csrfmiddlewaretoken')
const valutazione = document.getElementById('voto').getAttribute('value')
const box = document.getElementsByName('sceltabox')
const button = document.getElementById('aggiungispesa')
const ingredienti = document.getElementsByName('ingredienti')

const handelSelezioneStelle = (size) => {
    const children = form.children
    for (let i=0; i<children.length; i++){
        if(i <= size){
            children[i].classList.add('checked')
        } else {
            children[i].classList.remove('checked')
        }
    }
}

handelSelezioneStelle(valutazione)


const handleselect = (selezione) => {
    switch(selezione){
        case 'uno':{
            handelSelezioneStelle(1)
            return  
        }
        case 'due':{
            handelSelezioneStelle(2)
            return
        }
        case 'tre':{
            handelSelezioneStelle(3)
            return
        }
        case 'quattro':{
            handelSelezioneStelle(4)
            return
        }
        case 'cinque':{
            handelSelezioneStelle(5)
            return
        }
    }
}

const getValore = (stringValue) => {
    let numero;
    if (stringValue === 'uno'){
        numero = 1
    } 
    else if (stringValue === 'due'){
        numero = 2
    } else if (stringValue === 'tre'){
        numero = 3
    } else if (stringValue === 'quattro'){
        numero = 4
    } else if (stringValue === 'cinque'){
        numero = 5
    } else {
        numero = 0
    } 
    return numero
    }


if (uno) {
    const arr = [uno, due, tre, quattro, cinque]
    arr.forEach(item=> item.addEventListener('mouseover', (event)=>{
        handleselect(event.target.id)
    }))    

    arr.forEach(item=> item.addEventListener('click', (event)=>{
        const val = event.target.id
        console.log(val)
        form.addEventListener('submit', e=>{
            e.preventDefault()
            const id = e.target.id
            const valore = getValore(val)

            $.ajax({
                type: 'POST',
                url: '/valuta_ricetta/',
                data: {
                    'csrfmiddlewaretoken' : csrf[0].value,
                    'r_id': id,
                    'val': valore
                },
                success: function(response){
                    console.log(response)
                    conferma.innerHTML = '<h6>Valutata con '+ response.score +'!</h6>'
                },
                error: function(error){
                    console.log(error)
                    conferma.innerHTML = '<h6>Ops.. Qualcosa è andato storto </h6>'
                }
            })

        })
    }))
}

box.forEach(item => item.addEventListener('click', (event)=>{
    var verifica = 0
    for (const element of box){
        if (element.checked){
            verifica = 1
        }
    }
    if (verifica == 1){
        button.removeAttribute("hidden")
    } else  {
        button.setAttribute("hidden", true)
    }
}))

button.addEventListener('click', (event)=>{
    var dict = {}
    for (const element of box){
        if (element.checked){
            q = element.nextSibling.nextSibling.value
            i = element.nextSibling.nextSibling.nextSibling.value
            dict[i] = q
        }
    }

    $.ajax({
        type: 'POST',
        url: '/aggiungispesa/',
        data: {
            'csrfmiddlewaretoken' : csrf[0].value,
            'dizionario': JSON.stringify(dict),
        },
        success: function(response){
            console.log(response)
            window.location.reload()
            return 
        },
        error: function(error){
            console.log(error)
        }
    })

})