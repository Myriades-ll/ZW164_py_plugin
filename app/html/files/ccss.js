class ArrayOfNumbers extends Array {
    constructor() {
        super();
    }

    /**
     * 
     * @param {Array<any>} item 
     * @returns {boolean}
     */
    isFiniteArray(item) {
        if (item instanceof Array) {
            return item.reduce(
                (accumulator, currentValue) => { return accumulator &&= isFinite(currentValue) },
                true
            )
        }
        return false
    }

    /**
     * @param {number | Array<number>} item
     */
    pushNumber(item) {
        if (item instanceof Array) {
            if (this.isFiniteArray(item)) this.push(...item);
            else throw new Error("Not number values " + item)
        } else {
            item *= 1;
            if (isFinite(item)) this.push(item);
        }
    }

    /**
     * @returns {number} the sum of all values
     */
    sum() {
        return this.reduce(
            (accumulator, currentValue) => {
                return accumulator + currentValue;
            }, 0
        )
    }

    /**
     * @returns {number} the number of values that are non zeros
     */
    non_zeros() {
        return this.reduce(
            (accumulator, currentValue) => {
                return currentValue > 0 ? accumulator + 1 : accumulator;
            }, 0
        )
    }

    log() {
        console.log(this);
    }
}

class Courbe {
    #canvas_height;
    #canvas_width;
    #context;
    #heights;

    /**
     * @param {HTMLCanvasElement} canvas
     */
    constructor(canvas) {
        this.canvas = canvas;
        if (this.#is_canvas()) {
            this.#context = this.canvas.getContext('2d');
            this.#canvas_height = this.canvas.height;
            this.#canvas_width = this.canvas.width;
            this.#heights.push(...[
                0,
                0,
                this.#canvas_height,
                this.#canvas_height
            ])
            this.#init();
        }
    }

    #is_canvas() {
        return this.canvas instanceof HTMLCanvasElement;
    }

    #init() {
        this.redraw([1, 1, 1, 1]);
    }

    /**
     * @param {number} value
     * @param {number} min
     * @param {number} max
     */
    #normalize_value(value, min, max) {
        return Math.max(Math.min(value, max), min);
    }

    /**
     * 
     * @param {Array<number>} timed_values 
     */
    redraw(timed_values) {
        if (this.#is_canvas()) {
            this.#context.clearRect(0, 0, this.#canvas_width, this.#canvas_height);
            this.#context.beginPath();
            this.#context.strokeStyle = "red";
            // first point; fixed
            this.#context.moveTo(0, this.#canvas_height);
            // building next points
            let deltas = new ArrayOfNumbers();
            deltas.pushNumber(timed_values);
            let total_time = deltas.sum();
            console.log('total time', total_time);
            deltas.log();
            deltas.forEach(
                (item, index) => {
                    this.#context.lineTo(
                        (index + 1) * this.#canvas_width * item / total_time,
                        this.#heights[index]
                    );
                }
            )
            // last point; fixed
            this.#context.lineTo(this.#canvas_width, this.#canvas_height);
            this.#context.stroke();
        }
    }
}

let courbe = new Courbe(document.getElementById('draw'));