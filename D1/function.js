let curInput='';
let curOp='';
let prevInput='';
let expectedSequence = [];
let currentSequenceIndex = 0;

let run = 0; 

let results = [];
let currentRunData=[];
let lastKeyPressTime = null;
let lastKeyPosition = null;
const keyWidth = 60;

function isExpectedInput(input) {
    // Hier kannst du Bedingungen anpassen, je nachdem, was du erwartest
    if (input !== expectedSequence[currentSequenceIndex]) {
        return false; // Verhindert "=", wenn eine Zahl fehlt
    }
    return true; // Standardmäßig erlauben wir alle anderen Eingaben
}

//Zufällige Zahlen 
function randomNum(){
    const num1 = (Math.random() * 10).toFixed(2);
    const num2 = (Math.random() * 10).toFixed(2);
    document.getElementById('randomNum').innerHTML=`Mulitply ${num1} with ${num2}`;
    document.getElementById('runs').innerHTML=`Runs: ${run}`;

    expectedSequence = [...num1.toString(), "*", ...num2.toString(), "="];
    currentSequenceIndex = 0;

    return {num1, num2};
}

//Zahl aufrufen 
function appendNum(num){
    if (!isExpectedInput(num)) return;

    const btn = document.getElementById('b' + (num === '.' ? '.' : num));
    logKeyPress(btn, num);

    //max 1 . darf vorkommen 
    if (num==='.'&& curInput.includes('.')) return;

    //max 2 Nachkommastellen
    if(curInput.includes('.')){
        //spltee Num an dem . und speicher dir die nachkommastellen 
        const decimals = curInput.split('.')[1];
        if (decimals.length>=2) return;
    }

    curInput+=num;
    document.getElementById('display').value =`${prevInput}${curOp}${curInput}`;
    currentSequenceIndex++;
}

//Operation aufrufen 
function appendOp(op) {
    if (!isExpectedInput(op)) return;

    const opBtn = document.querySelector(`.operator`);
    logKeyPress(opBtn, op);
    
    if (curInput === '') return;
    if (prevInput !== '') {
        calculate(); 
    }
    curOp = op;
    prevInput = curInput;
    curInput = '';
    document.getElementById('display').value = `${prevInput} ${curOp}`;
    
    currentSequenceIndex++;
}

//Rechner
function calculate() {
    if (!isExpectedInput("=")) return;

    const equalBtn = document.querySelector('.equal');
    logKeyPress(equalBtn, '=');

    if (prevInput === '' || curInput === '') return;
    let result;
    let prev = parseFloat(prevInput);
    let cur = parseFloat(curInput);

    result = prev * cur;
    
    curInput = (typeof result === 'number') ? result.toFixed(2) : result;
    curOp = '';
    prevInput = '';
    document.getElementById('display').value = curInput;

    currentSequenceIndex++;

    results.push({
        run: run,
        data: currentRunData
    });

    currentRunData = [];

    clearForNewCalc();
}

function clearForNewCalc(){
    sleep(2000).then (()=> {
    document.getElementById('display').value =``;
    expectedSequence = [];
    currentSequenceIndex = 0;
    curInput = '';
    prevInput = '';
    curOp = '';
    lastKeyPressTime = null;
    lastKeyPosition = null;
    run++;
    randomNum();
    });
}

function sleep(ms){
    return new Promise(resolve => setTimeout(resolve, ms));
}

//Distanz zw. zwei Tasten 
function calculateDistance(elem1, elem2) {
    const rect1 = elem1.getBoundingClientRect();
    const rect2 = elem2.getBoundingClientRect();

    const x1 = rect1.left + rect1.width / 2;
    const y1 = rect1.top + rect1.height / 2;

    const x2 = rect2.left + rect2.width / 2;
    const y2 = rect2.top + rect2.height / 2;

    const distance = Math.hypot(x2 - x1, y2 - y1);
    return distance;
}

function calculateID(d, w) {
    return Math.log2((2 * d) / w);
}

//benötigte Zeit 
function logKeyPress(buttonElement, label) {
    const currentTime = Date.now();
    let mt = 0;
    let id = 0;

    if (lastKeyPressTime !== null && lastKeyPosition !== null) {
        mt = (currentTime - lastKeyPressTime) / 1000; // Sekunden
        const D = calculateDistance(lastKeyPosition, buttonElement);
        id = calculateID(D, keyWidth);
    }

    currentRunData.push({
        key: label,
        MT: mt,
        ID: id
    });

    lastKeyPressTime = currentTime;
    lastKeyPosition = buttonElement;
}

function saveResults() {
    // JSON formatieren
    const json = JSON.stringify(results, null, 2);

    // Blob für den Download erstellen
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);

    // Download-Link erzeugen
    const a = document.createElement('a');
    a.href = url;
    a.download = 'reaction_results_' + 
        new Date().toISOString().slice(0, 19).replace(/:/g, '-') + 
        '.json';
    
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    // Speicher freigeben
    URL.revokeObjectURL(url);
}

window.onload = function() {
    randomNum();
}
