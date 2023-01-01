class Line {
    constructor(point_0, point_1) {
        this.point_0 = point_0;
        this.point_1 = point_1;
    }
}

class Courbe {

    constructor(canvas) {
        this.canvas = canvas;
        this.context = this.canvas.getContext('2d');
        this.canvas_height = this.canvas.height;
        this.canvas_width = this.canvas.width;
        this.init();
    }

    init() {
        this.redraw([5, 1, 5, 1]);
    }

    redraw(timed_values) {
        this.context.clearRect(0, 0, this.canvas_width, this.canvas_height);
        this.context.moveTo(0, this.canvas_height);
        timed_values.forEach(
            function (item, index, array) {
                console.log(item);
                console.log(index);
                console.log(array);
            }
        );
        this.context.stroke();
    }
}

let courbe = new Courbe(document.getElementById('draw'));