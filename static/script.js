let currentPatient = "";

/* ---------------- ONLINE / OFFLINE STATUS ---------------- */

function updateStatus(){

let status = document.getElementById("statusBar");
if(!status) return;

/* Check internet first */

if(!navigator.onLine){

status.innerText = "OFFLINE MODE";
status.style.background = "red";
return;

}

/* If internet available check server */

fetch("/status")
.then(r => r.json())
.then(data => {

status.innerText = "ONLINE MODE";
status.style.background = "green";

})
.catch(()=>{

status.innerText = "SERVER OFFLINE";
status.style.background = "orange";

});

}

/* detect wifi changes */

window.addEventListener("online", updateStatus);
window.addEventListener("offline", updateStatus);
/* ---------------- ADD PATIENT ---------------- */

function addPatient(){

fetch("/add_patient",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({
id:document.getElementById("pid").value,
name:document.getElementById("pname").value,
age:document.getElementById("page").value,
mobile:document.getElementById("pmobile").value,
problem:document.getElementById("pproblem").value
})
})
.then(()=>{

alert("Patient Saved");

document.getElementById("pid").value="";
document.getElementById("pname").value="";
document.getElementById("page").value="";
document.getElementById("pmobile").value="";
document.getElementById("pproblem").value="";

})
.catch(err => console.log(err));

}

/* ---------------- ADD TOKEN MANUALLY ---------------- */

function addQueue(){

fetch("/add_queue",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({
patient_id:document.getElementById("qid").value
})
})
.then(loadQueue)
.catch(err => console.log(err));

}

/* ---------------- LOAD QUEUE ---------------- */

function loadQueue(){

fetch("/get_queue")
.then(r => r.json())
.then(data => {

let q = document.getElementById("queue");
if(!q) return;

q.innerHTML = "";

if(data.length === 0){
q.innerHTML = "<p>No patients in queue</p>";
return;
}

data.forEach(i => {

let div = document.createElement("div");
div.className = "queue-item";

div.innerText = "Token " + i.token + " - " + i.name;

div.onclick = function(){
showPatient(i.patient_id);
};

q.appendChild(div);

});

})
.catch(err => console.log(err));

}

/* ---------------- SHOW PATIENT DETAILS ---------------- */

function showPatient(pid){

fetch("/get_patient/" + pid)
.then(r => r.json())
.then(p => {

currentPatient = p.id;

document.getElementById("id").innerText = p.id;
document.getElementById("name").innerText = p.name;
document.getElementById("age").innerText = p.age;
document.getElementById("mobile").innerText = p.mobile;
document.getElementById("problem").innerText = p.problem;

document.getElementById("notes").value = p.notes;

})
.catch(err => console.log(err));

}

/* ---------------- SAVE DOCTOR NOTES ---------------- */

function saveNotes(){

fetch("/save_notes",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({
id:currentPatient,
notes:document.getElementById("notes").value
})
})
.then(()=> alert("Notes Saved"))
.catch(err => console.log(err));

}

/* ---------------- NEXT PATIENT ---------------- */

function nextPatient(){

fetch("/next_patient",{method:"POST"})
.then(loadQueue)
.catch(err => console.log(err));

}

/* ---------------- START SYSTEM ---------------- */

document.addEventListener("DOMContentLoaded", function(){

updateStatus();

loadQueue();

/* auto refresh queue every 3 seconds */
setInterval(loadQueue,3000);
setInterval(updateStatus,3000);

});
