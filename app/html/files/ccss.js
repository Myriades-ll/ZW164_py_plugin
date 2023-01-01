class Point {
    constructor(x_pos) {
        this.x_pos = x_pos;
        this.y_pos = 0;
    }
}
class Line {
    constructor(point_0, point_1) {
        this.point_0 = point_0;
        this.point_1 = point_1;
    }
}

class Courbe {

    #canvas_height = 0;
    #canvas_width = 0;
    #context = undefined;
    constructor(canvas) {
        this.canvas = canvas;
        this.#context = this.canvas.getContext('2d');
        this.#canvas_height = this.canvas.height;
        this.#canvas_width = this.canvas.width;
        this.#init();
    }

    #init() {
        this.redraw([5, 1, 5, 1]);
    }

    #normalize_value(value, min, max) {
        return Math.max(Math.min(value, min), max);
    }

    redraw(timed_values) {
        this.context.clearRect(0, 0, this.canvas_width, this.canvas_height);
        // first point; fixed
        this.context.moveTo(0, this.canvas_height);
        let deltas = [];
        timed_values.forEach(
            (item, index) => {
                let delta_time = 0.0;
                // normalize time periods
                if (index % 2 == 0) {// 20ms; from 0 to 127
                    delta_time += this.#normalize_value(item, 0, 127) * 0.02;
                } else {// 100ms; from 0 to 255
                    delta_time += this.#normalize_value(item, 0, 255) * 0.1;
                }
                deltas.push(delta_time)
            }
        );
        let total_time = deltas.reduce(
            function (accumulator, currentValue) {
                accumulator + currentValue
            },
            0
        )
        console.log(total_time);
        // last point; fixed
        this.#context.moveTo(this.#canvas_width, this.#canvas_height);
        this.context.stroke();
    }
}

let courbe = new Courbe(document.getElementById('draw'));