class ArrayOfNumbers extends Array {
    constructor() {
        super();
    }

    pushNumber(item) {
        item *= 1;
        if (isFinite(item)) this.push(item);
    }

    sum() {
        return this.reduce(
            function (accumulator, currentValue) {
                return accumulator + currentValue;
            }, 0
        )
    }

    non_zeros() {
        return this.reduce(
            function (accumulator, currentValue) {
                if (currentValue > 0) {
                    return accumulator + 1;
                }
                return accumulator;
            }, 0
        )
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
        return Math.max(Math.min(value, max), min);
    }

    redraw(timed_values) {
        this.#context.clearRect(0, 0, this.canvas_width, this.canvas_height);
        // first point; fixed
        let y_value = this.#canvas_height;
        this.#context.moveTo(0, y_value);
        let deltas = new ArrayOfNumbers();
        timed_values.forEach(
            (item, index) => {
                let delta_time = 0.0;
                // normalize time periods
                if (index % 2 == 0) {// 20ms; from 0 to 127
                    delta_time += this.#normalize_value(item, 0, 127) * 0.02;
                } else {// 100ms; from 0 to 255
                    delta_time += this.#normalize_value(item, 0, 255) * 0.1;
                }
                deltas.pushNumber(delta_time)
            }
        );
        let total_time = deltas.sum();
        let non_zeros = deltas.non_zeros();
        deltas.forEach(
            (item, index) => {
                if (y_value == 0) y_value = this.#canvas_height;
                else y_value = 0;
                this.#context.moveTo(
                    (index + 1) * this.#canvas_width / non_zeros,
                    y_value
                );
            }
        )
        console.log('total time', total_time);
        console.log('Non zeros values', non_zeros);
        // last point; fixed
        this.#context.moveTo(this.#canvas_width, this.#canvas_height);
        this.#context.stroke();
    }
}

let courbe = new Courbe(document.getElementById('draw'));