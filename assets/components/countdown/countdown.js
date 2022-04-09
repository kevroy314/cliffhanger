const FULL_DASH_ARRAY = 283;
const WARNING_THRESHOLD = 60;
const ALERT_THRESHOLD = 30;

const COLOR_CODES = {
  info: {
    color: "green"
  },
  warning: {
    color: "orange",
    threshold: WARNING_THRESHOLD
  },
  alert: {
    color: "red",
    threshold: ALERT_THRESHOLD
  }
};

const TIME_LIMIT = 60*15;
let timePassed = 0;
let timeLeft = TIME_LIMIT;
let timerInterval = null;
let play = 0;
let remainingPathColor = COLOR_CODES.info.color;
let previous_state = false;

function initialize(){
    document.getElementById("countdown-timer").innerHTML = `
    <div class="base-timer"">
    <svg class="base-timer__svg" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
        <g class="base-timer__circle">
        <circle class="base-timer__path-elapsed" cx="50" cy="50" r="45"></circle>
        <path
            id="base-timer-path-remaining"
            stroke-dasharray="283"
            class="base-timer__path-remaining ${remainingPathColor}"
            d="
            M 50, 50
            m -45, 0
            a 45,45 0 1,0 90,0
            a 45,45 0 1,0 -90,0
            "
        ></path>
        </g>
    </svg>
    <span id="base-timer-label" class="base-timer__label">${formatTime(
        timeLeft
    )}</span><button class='button' id="pause-play-icon" onclick="timer_click();"></button>
    <svg class="reset-button" id="reset-button" onclick="reset_counter();" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--! Font Awesome Pro 6.1.1 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2022 Fonticons, Inc. --><path d="M480 256c0 123.4-100.5 223.9-223.9 223.9c-48.86 0-95.19-15.58-134.2-44.86c-14.14-10.59-17-30.66-6.391-44.81c10.61-14.09 30.69-16.97 44.8-6.375c27.84 20.91 61 31.94 95.89 31.94C344.3 415.8 416 344.1 416 256s-71.67-159.8-159.8-159.8C205.9 96.22 158.6 120.3 128.6 160H192c17.67 0 32 14.31 32 32S209.7 224 192 224H48c-17.67 0-32-14.31-32-32V48c0-17.69 14.33-32 32-32s32 14.31 32 32v70.23C122.1 64.58 186.1 32.11 256.1 32.11C379.5 32.11 480 132.6 480 256z"/></svg>
    </div>
    </div>
    `;

    startTimer();
}

function attempt_initialization(){
    // look for rising edge where interval triggers and previous iterations
    // did not contain the countdown-timer, but current iteration does
    // in this case, initialize the element properties
    var element_exists = !(document.getElementById("countdown-timer") === null);
    if (element_exists && !previous_state)
        initialize();
    previous_state = element_exists;
}

setInterval(attempt_initialization, 500);

previous_confirmation_text = ""
function detect_server_reset_request(){
  var confirmation_text = document.getElementById("confirmation-text").innerHTML;
  if (confirmation_text) {
    if (previous_confirmation_text != confirmation_text){
      reset_counter();
      play = 0;
    }
    previous_confirmation_text = confirmation_text
  }
}

setInterval(detect_server_reset_request, 500);

function onTimesUp() {
  clearInterval(timerInterval);
}

function startTimer() {
  
  timerInterval = setInterval(() => {
    timePassed = timePassed += (1 * play);
    timeLeft = TIME_LIMIT - timePassed;
    document.getElementById("base-timer-label").innerHTML = formatTime(
      timeLeft
    );
    setCircleDasharray();
    setRemainingPathColor(timeLeft);

    if (timeLeft === 0) {
      onTimesUp();
    }
  }, 1000);
}

function formatTime(time) {
  const minutes = Math.floor(time / 60);
  let seconds = time % 60;

  if (seconds < 10) {
    seconds = `0${seconds}`;
  }

  return `${minutes}:${seconds}`;
}

function setRemainingPathColor(timeLeft) {
  const { alert, warning, info } = COLOR_CODES;
  if (timeLeft <= alert.threshold) {
    document
      .getElementById("base-timer-path-remaining")
      .classList.remove(warning.color);
    document
      .getElementById("base-timer-path-remaining")
      .classList.add(alert.color);
  } else if (timeLeft <= warning.threshold) {
    document
      .getElementById("base-timer-path-remaining")
      .classList.remove(info.color);
    document
      .getElementById("base-timer-path-remaining")
      .classList.add(warning.color);
  }
}

function calculateTimeFraction() {
  const rawTimeFraction = timeLeft / TIME_LIMIT;
  return rawTimeFraction - (1 / TIME_LIMIT) * (1 - rawTimeFraction);
}

function setCircleDasharray() {
  const circleDasharray = `${(
    calculateTimeFraction() * FULL_DASH_ARRAY
  ).toFixed(0)} 283`;
  document
    .getElementById("base-timer-path-remaining")
    .setAttribute("stroke-dasharray", circleDasharray);
}

function timer_click() {
  var btn = document.getElementById("pause-play-icon");
  btn.classList.toggle("paused");
  play = (play + 1) % 2;
}

function reset_reset_button() {
  reset_btn = document.getElementById("reset-button");
  if (reset_btn.classList.contains('animate-reset-button'))
    reset_btn.classList.toggle('animate-reset-button');
}

function reset_counter() {
  timePassed = 0;
  timeLeft = TIME_LIMIT - timePassed;
  document.getElementById("base-timer-label").innerHTML = formatTime(
      timeLeft
    );
  document.getElementById("reset-button").classList.toggle('animate-reset-button');
  setTimeout(reset_reset_button, 100);
}