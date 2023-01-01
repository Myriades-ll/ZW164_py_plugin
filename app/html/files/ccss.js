class Courbe {

    constructor(canvas) {
        this.canvas = canvas;
        this.context = this.canvas.getContext('2d');
    }

    draw() {
        ctx.moveTo(0, 100);
        ctx.lineTo(100, 0);
        ctx.lineTo(200, 0);
        ctx.lineTo(300, 100);
        ctx.lineTo(400, 100);
        ctx.stroke();
    }
}

let courbe = new Courbe(document.getElementById('draw'));
courbe.draw();