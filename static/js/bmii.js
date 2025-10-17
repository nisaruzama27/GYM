function bb() {
  var w = document.forms["bodymass"]["w"].value;
  var h = document.forms["bodymass"]["h"].value;
  var ww = parseFloat(w);
  var hh = parseFloat(h);

  if (isNaN(ww) || isNaN(hh) || ww <= 0 || hh <= 0) {
    alert("Please enter valid positive numbers for weight and height.");
    return;
  }

  var m = (hh / 100) * (hh / 100); // height in meters squared
  var result = ww / m;

  alert("Your BMI is: " + result.toFixed(1));
}