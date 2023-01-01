var canvas = document.getElementById('draw');
console.log(canvas);
var ctx = canvas.getContext("2d");
ctx.moveTo(0, 100);
ctx.lineTo(100, 0);
ctx.lineTo(200, 0);
ctx.lineTo(300, 100);
ctx.lineTo(400, 100);
ctx.stroke();
