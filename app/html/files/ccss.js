var canvas = document.getElementById('draw');
console.log(canvas);
var ctx = canvas.getContext("2d");
ctx.moveTo(0, 0);
ctx.lineTo(200, 100);
ctx.stroke();
