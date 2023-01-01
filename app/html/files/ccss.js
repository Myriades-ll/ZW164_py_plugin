class Courbe {

    constructor(canvas) {
        this.canvas = canvas;
        this.context = this.canvas.getContext('2d');
    }

    draw() {
        this.context.moveTo(0, 100);
        this.context.lineTo(100, 0);
        this.context.lineTo(200, 0);
        this.context.lineTo(300, 100);
        this.context.lineTo(400, 100);
        this.context.stroke();
    }
}

let courbe = new Courbe(document.getElementById('draw'));
courbe.draw();