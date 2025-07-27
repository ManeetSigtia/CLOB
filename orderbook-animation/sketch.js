// --- NEW: Professional Recruiter-Focused Color Palette ---
const PALETTE = {
  BACKGROUND: "#0d1117", // GitHub dark mode background
  TEXT_PRIMARY: "#e6edf3", // Main text (bright white)
  TEXT_SECONDARY: "#7d8590", // Muted text for heap lines and details
  STATUS_TEXT: "#22a0f0", // A bright, clean cyan for main status updates

  // A cohesive blue/purple theme for the order books
  BID_PRIMARY: "#0d47a1", // Deep, professional blue
  BID_SECONDARY: "#42a5f5", // Lighter, vibrant blue for accents

  ASK_PRIMARY: "#6a1b9a", // Deep, professional purple
  ASK_SECONDARY: "#ab47bc", // Lighter, vibrant purple for accents
};

// --- Data Structure Classes ---

class Order {
  constructor(id, qty) {
    this.id = id;
    this.qty = qty;
    // Animation properties
    this.displayQty = qty;
    this.alpha = 255;
  }
}

class PriceLevel {
  constructor(price) {
    this.price = price;
    this.totalQuantity = 0;
    this.orders = [];
    this.idToOrderMap = new Map();
    // Animation properties
    this.alpha = 0; // Start invisible
    this.isFadingOut = false;
  }

  // --- Animation Methods ---
  fadeIn() {
    this.alpha = 255;
  }

  startFadeOut() {
    this.isFadingOut = true;
  }

  // Animate values towards their targets over time
  updateAnimations() {
    if (this.isFadingOut) {
      this.alpha = lerp(this.alpha, 0, 0.1);
    } else if (this.alpha < 255) {
      this.alpha = lerp(this.alpha, 255, 0.1);
    }

    let currentTotal = 0;
    for (const order of this.orders) {
      order.displayQty = lerp(order.displayQty, order.qty, 0.1);
      currentTotal += order.displayQty;
    }
    this.totalQuantity = currentTotal;
  }

  // --- Data Methods ---
  addOrder(id, qty) {
    const order = new Order(id, qty);
    order.displayQty = order.qty;
    order.alpha = 255;
    this.orders.push(order);
    this.idToOrderMap.set(id, order);
  }

  removeOrder(id) {
    this.orders = this.orders.filter((order) => order.id !== id);
    this.idToOrderMap.delete(id);
  }

  updateOrder(id, newQty) {
    const orderToUpdate = this.idToOrderMap.get(id);
    if (orderToUpdate) {
      orderToUpdate.qty = newQty; // Set target qty
    }
  }

  // --- Drawing Method ---
  draw(x, y, bookType) {
    this.updateAnimations();
    if (this.alpha < 1) return; // Don't draw if invisible

    const isBid = bookType === "bid";
    const primaryColor = isBid ? PALETTE.BID_PRIMARY : PALETTE.ASK_PRIMARY;
    const secondaryColor = isBid
      ? PALETTE.BID_SECONDARY
      : PALETTE.ASK_SECONDARY;

    stroke(
      red(secondaryColor),
      green(secondaryColor),
      blue(secondaryColor),
      this.alpha
    );
    strokeWeight(2);
    fill(
      red(PALETTE.BACKGROUND),
      green(PALETTE.BACKGROUND),
      blue(PALETTE.BACKGROUND),
      this.alpha
    );
    ellipse(x, y, 150, 50);

    noStroke();
    fill(
      red(PALETTE.TEXT_PRIMARY),
      green(PALETTE.TEXT_PRIMARY),
      blue(PALETTE.TEXT_PRIMARY),
      this.alpha
    );
    textAlign(CENTER, CENTER);
    textSize(14);
    text(`Price: ${this.price}\nQty: ${this.totalQuantity.toFixed(0)}`, x, y);

    let orderX = x + 120;
    const orderY = y;
    for (let i = 0; i < this.orders.length; i++) {
      const order = this.orders[i];

      strokeWeight(1.5);
      stroke(
        red(secondaryColor),
        green(secondaryColor),
        blue(secondaryColor),
        this.alpha
      );
      fill(
        red(primaryColor),
        green(primaryColor),
        blue(primaryColor),
        this.alpha
      );
      circle(orderX, orderY, 40);

      noStroke();
      fill(
        red(PALETTE.TEXT_PRIMARY),
        green(PALETTE.TEXT_PRIMARY),
        blue(PALETTE.TEXT_PRIMARY),
        this.alpha
      );
      textSize(10);
      text(`ID:${order.id}\nQ:${order.displayQty.toFixed(1)}`, orderX, orderY);

      if (i < this.orders.length - 1) {
        let arrowColorNext = color(PALETTE.BID_SECONDARY); // 'Next' arrow is always the 'buy' color
        let arrowColorPrev = color(PALETTE.ASK_SECONDARY); // 'Prev' arrow is always the 'sell' color
        arrowColorNext.setAlpha(this.alpha);
        arrowColorPrev.setAlpha(this.alpha);
        drawArrow(orderX + 22, orderY, orderX + 58, orderY, arrowColorNext);
        drawArrow(
          orderX + 58,
          orderY + 6,
          orderX + 22,
          orderY + 6,
          arrowColorPrev
        );
      }
      orderX += 80;
    }
  }
}

// --- Global Variables ---
let bidBook = [];
let askBook = [];

let actionQueue = [];
let pauseDurations = [];
let currentActionIndex = 0;
let lastActionTime = 0;
let statusMessage = "Starting...";
let preActionMessage = "";

// --- Core p5.js Functions ---

function setup() {
  createCanvas(1400, 700);

  const steps = [
    {
      status: "Step 1: Place Bid B1",
      details: "Action: Place | ID:1, P:100, Q:10",
      animate: () => placeOrder(bidBook, 1, 100, 10, "bid"),
    },
    {
      status: "Step 2: Place Bid B2",
      details: "Action: Place | ID:2, P:101, Q:5",
      animate: () => placeOrder(bidBook, 2, 101, 5, "bid"),
    },
    {
      status: "Step 3: Place Ask A1",
      details: "Action: Place | ID:4, P:103, Q:15",
      animate: () => placeOrder(askBook, 4, 103, 15, "ask"),
    },
    {
      status: "Step 4: Place Bid B3",
      details: "Action: Place | ID:3, P:101, Q:15",
      animate: () => placeOrder(bidBook, 3, 101, 5, "bid"),
    },
    {
      status: "Step 5: Place Ask A2",
      details: "Action: Place | ID:5, P:104, Q:15",
      animate: () => placeOrder(askBook, 5, 104, 15, "ask"),
    },
    {
      status: "Step 6: Place Ask A3",
      details: "Action: Place | ID:6, P:105, Q:15",
      animate: () => placeOrder(askBook, 6, 105, 15, "ask"),
    },
    {
      status: "Step 7: Cancel Order",
      details: "Action: Cancel | ID:4",
      animate: () => cancelOrder(askBook, 4, 103),
      finalize: () => finalizeRemove(askBook, 103),
    },
    {
      status: "Step 8: Place Ask 4 - Partial Match",
      details:
        "Action: Place | ID:6, P:101, Q:3 & Match | Update ID:2, New Q:2",
      animate: () => partialMatch(bidBook, 2, 101, 2),
    },
    {
      status: "Step 9: Incoming Market Order",
      details: "Market BID for 25 units",
      animate: () => {},
    },
    {
      status: "Step 10: Matching Best Ask",
      details: "Match vs P:104 (15 units). Remaining: 10",
      animate: () => cancelOrder(askBook, 5, 104),
      finalize: () => finalizeRemove(askBook, 104),
    },
    {
      status: "Step 11: Matching Final Ask",
      details: "Match vs P:105 (10 units). Remaining: 0",
      animate: () => partialMatch(askBook, 6, 105, 5),
      finalize: () => {},
    },
    {
      status: "Animation Complete",
      details: "Refresh to restart.",
      animate: () => {},
    },
  ];

  const ANNOUNCE_PAUSE = 1500;
  const ANIMATION_PAUSE = 1000;
  const OBSERVE_PAUSE = 2000;

  steps.forEach((step) => {
    // 1. Announce
    actionQueue.push(() => {
      statusMessage = step.status;
      preActionMessage = step.details;
    });
    pauseDurations.push(ANNOUNCE_PAUSE);

    // 2. Trigger Animation
    actionQueue.push(() => {
      if (step.animate) step.animate();
      preActionMessage = ""; // Clear details text
    });
    pauseDurations.push(ANIMATION_PAUSE);

    // 3. Finalize State
    actionQueue.push(() => {
      if (step.finalize) step.finalize();
    });
    pauseDurations.push(OBSERVE_PAUSE);
  });

  lastActionTime = millis();
  actionQueue[0]();
}

function draw() {
  background(PALETTE.BACKGROUND);

  if (millis() - lastActionTime > pauseDurations[currentActionIndex]) {
    if (currentActionIndex < actionQueue.length - 1) {
      currentActionIndex++;
      actionQueue[currentActionIndex]();
      lastActionTime = millis();
    }
  }

  fill(PALETTE.TEXT_PRIMARY);
  textAlign(CENTER, CENTER);
  textSize(20);
  text("BID BOOK (Max Heap)", width * 0.25, 30);
  text("ASK BOOK (Min Heap)", width * 0.75, 30);

  if (bidBook.length > 0)
    drawHeapTree(bidBook, 0, width * 0.25, 80, width / 8, "bid");
  if (askBook.length > 0)
    drawHeapTree(askBook, 0, width * 0.75, 80, width / 8, "ask");

  fill(PALETTE.TEXT_SECONDARY); // Muted grey for details
  textSize(16);
  text(preActionMessage, width / 2, height - 60);

  fill(PALETTE.STATUS_TEXT); // Bright cyan for status
  textSize(18);
  text(statusMessage, width / 2, height - 30);
}

// --- Drawing Helpers ---

function drawHeapTree(book, index, x, y, xSpacing, bookType) {
  if (index >= book.length) return;

  book[index].draw(x, y, bookType);

  let leftChildIndex = 2 * index + 1;
  let rightChildIndex = 2 * index + 2;

  const currentAlpha = book[index].alpha;
  if (currentAlpha < 1) return;

  let lineCol = color(PALETTE.TEXT_SECONDARY);
  lineCol.setAlpha(currentAlpha);

  if (leftChildIndex < book.length) {
    let childX = x - xSpacing;
    let childY = y + 100;
    stroke(lineCol);
    strokeWeight(1.5);
    line(x, y + 25, childX, childY - 25);
    drawHeapTree(book, leftChildIndex, childX, childY, xSpacing / 2, bookType);
  }

  if (rightChildIndex < book.length) {
    let childX = x + xSpacing;
    let childY = y + 100;
    stroke(lineCol);
    strokeWeight(1.5);
    line(x, y + 25, childX, childY - 25);
    drawHeapTree(book, rightChildIndex, childX, childY, xSpacing / 2, bookType);
  }
}

function drawArrow(x1, y1, x2, y2, color) {
  push();
  stroke(color);
  strokeWeight(1.5);
  fill(color);
  line(x1, y1, x2, y2);
  let angle = atan2(y2 - y1, x2 - x1);
  translate(x2, y2);
  rotate(angle);
  triangle(0, 0, -6, -3, -6, 3);
  pop();
}

// --- Order Book Operations ---

function placeOrder(book, id, price, qty, type) {
  let level = book.find((p) => p.price === price);
  if (!level) {
    level = new PriceLevel(price);
    book.push(level);
  }
  level.addOrder(id, qty);

  if (type === "bid") {
    book.sort((a, b) => b.price - a.price);
  } else {
    book.sort((a, b) => a.price - b.price);
  }
}

function cancelOrder(book, id, price) {
  let level = book.find((p) => p.price === price);
  if (level) {
    level.startFadeOut();
  }
}

function partialMatch(book, id, price, finalQty) {
  let level = book.find((p) => p.price === price);
  if (level) {
    level.updateOrder(id, finalQty);
  }
}

function finalizeRemove(book, price) {
  if (book === bidBook) {
    bidBook = bidBook.filter((l) => l.price !== price);
  } else {
    askBook = askBook.filter((l) => l.price !== price);
  }
}
