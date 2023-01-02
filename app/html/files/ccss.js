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
        console.log(item);
        if (item instanceof Array) {
            console.log('item is an array');
            if (this.isFiniteArray(item)) this.push(...item);
            else throw new Error("Not number values " + item)
        } else {
            console.log('item is other');
            item *= 1;
            if (isFinite(item)) this.push(item);
        }
        this.log();
    }

    /**
     * @returns {number} the sum of all values
     */
    sum() {
        return this.reduce(
            (accumulator, currentValue) => {
                console.log('sum()', accumulator, currentValue);
                accumulator + currentValue;
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

    /**
     * @param {HTMLCanvasElement} canvas
     */
    constructor(canvas) {
        this.canvas = canvas;
        if (this.#is_canvas()) {
            this.#context = this.canvas.getContext('2d');
            this.#canvas_height = this.canvas.height;
            this.#canvas_width = this.canvas.width;
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
            // first point; fixed
            let y_value = this.#canvas_height;
            this.#context.moveTo(0, y_value);
            let deltas = new ArrayOfNumbers();
            deltas.pushNumber(timed_values);
            let total_time = deltas.sum();
            let non_zeros = deltas.non_zeros();
            console.log('total time', total_time);
            console.log('Non zeros values', non_zeros);
            deltas.log();
            deltas.forEach(
                (item, index) => {
                    y_value == 0 ? y_value = this.#canvas_height : y_value = 0;
                    this.#context.moveTo(
                        (index + 1) * this.#canvas_width * item / total_time,
                        y_value
                    );
                }
            )
            // last point; fixed
            this.#context.moveTo(this.#canvas_width, this.#canvas_height);
            this.#context.stroke();
        }
    }
}

let courbe = new Courbe(document.getElementById('draw'));