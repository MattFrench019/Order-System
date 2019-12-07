// This work is licensed under the Creative Commons Attribution-ShareAlike 4.0 International License.
// To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/4.0/
// or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.

// Holds all of the stuff to manage the web-app
class Manager{

    // Takes divs to control the displaying of pages
    constructor(mainMenu, createOrder, orderList, chooseTable){
        this.main = mainMenu;       // Page for main menu
        this.menu = createOrder;    // Page to create order
        this.orderList = orderList; // Page to select order
        this.table = chooseTable;   // Choose a table

        this.tableNum = -1;         // Init table number
        this.order = []             // Init order array
    }

    // Private Method
    // Takes  a bool and decides whether to show/hide div
    _boolToDisplay(bool){
        if (bool === false){
            return 'none'
        }
        else if (bool === true){
            return 'block'
        }
    }

    // Private Method
    // Shows and hides the divs
    _goTo(main, menu, list, table){
        this.main.style.display = this._boolToDisplay(main);
        this.menu.style.display = this._boolToDisplay(menu);
        this.orderList.style.display = this._boolToDisplay(list);
        this.table.style.display = this._boolToDisplay(table);
    }

    // Private Method
    // Gets list of orders from the backend and pipes
    // the results into buttons on the order list page
    _populateOrderList(){

        // Makes the request
        $.ajax({

            // URL to backend
            url: 'orders/get/all',

            // Called on success
            success: function (data){

                // Gets the grid where the orders will be added to
                let list = document.getElementById("orders-page orders-grid");

                // Empties the existing items in the grid
                list.innerHTML = '';

                // Loops through all orders in the result
                data.forEach(function (item) {

                    // Creates a new button
                    let newItem = document.createElement('button');

                    // Sets the class to the correct button
                    newItem.className = 'orders-page order-button';

                    // Creates the id of the button
                    newItem.id = 'order-' + item[0];

                    // Assigns the onClick function of the button to the goToEditOrder function
                    newItem.onclick = function () {manager.goToEditOrder(item)};

                    // Adds text to the button
                    newItem.appendChild(document.createTextNode(item[3]));

                    // Adds the button to the grid
                    list.appendChild(newItem)
                })
            }
        });
    }

    // Goes to the main order page
    goToMain(){
        this._goTo(true, false, false, false);
    }

    // Goes to the choose-table page
    goToChooseTable(){
        this._goTo(false, false, false, true);
    }

    // Goes to the new order page
    goToNewOrder(id){

        // Gets the table number from the clicked button
        this.tableNum = id.split('-')[1];

        // This changes the behaviour of the save button
        this.editOrNew = 'new';

        // Changes the heading of the page
        document.getElementById('create-order order-title').innerText = 'New Order For Table ' + this.tableNum;

        // Resets the order list
        this.order = [];

        // Empties the grid which holds the current order items
        document.getElementById('create-order item-grid').innerHTML = '';

        // Go to the next page
        this._goTo(false, true, false, false);
    }

    // Goes to the new order page in edit mode
    goToEditOrder(item){

        // Item is an array which is the same as the one provided by the backend
        // Therefore it looks like:
        //  [<id>, <table>, [<item_id>, <item_name>], <readable>
        // Refer to Order.tuple for more documentation

        // Get table number
        this.tableNum = item[1];

        // Get the id of the order
        this.editOrder = item[0];

        // This changes the behaviour of the save button
        this.editOrNew = 'edit';

        // Change the heading
        document.getElementById('create-order order-title').innerText = 'Editing Order For Table ' + this.tableNum;

        // Reset the order list
        this.order = [];

        // Remove all items in the grid that keeps track of order items
        document.getElementById('create-order item-grid').innerHTML = '';

        // Adds each item in the order to the page using
        // existing logic, makes my life easier
        // .bind(this) allows me to access the Manager object within the loop
        item[2].forEach(function (order_item) {
            var itemId = order_item[0];
            var itemName = order_item[1];

            this._addItem(itemId, itemName);
        }.bind(this));

        // Go to the new order page
        this._goTo(false, true, false, false);
    }

    // Goes to the page which displays the list of orders
    goToOrderList(){

        // Populates the order list
        this._populateOrderList();

        // Go to the page
        this._goTo(false, false, true, false);
    }

    // Called by the buttons on the order page
    addItem(element){

        // Element id example:
        //  id-<id>&name-<name>

        // Gets the item id from the element id
        var itemId = element.id.split('&')[0].split('-')[1];

        // Gets the item name from the element is
        var itemName = element.id.split('&')[1].split('-')[1];

        // Add the item
        this._addItem(itemId, itemName)
    }

    // Holds logic to add the item
    _addItem(id, name){

        // Get the list that holds the order items
        const list = document.getElementById('create-order item-grid');

        // If there is none of the item in the order
        if (this.order.includes(id) === false){
            // Add new button

            // Create new button
            let newItem = document.createElement('button');

            // Set the class
            newItem.className = 'create-order item-grid-button';

            // Set the id of the button, allows me to see what item to remove
            newItem.id = 'itemgrid-' + id;

            // Set the function to point to the removeItem function with the element as a parameter
            newItem.onclick = function () {manager.removeItem(this)};

            // Add the text to display how many of the item there are
            newItem.appendChild(document.createTextNode(name + ' x 1'));

            // Add the button to the grid
            list.appendChild(newItem)
        }

        else if (this.order.includes(id) === true){
            // Edit existing button

            // Get the existing button
            let existingItem = document.getElementById('itemgrid-' + id);

            // Change the text to the current number + 1
            existingItem.innerText = name + ' x ' + (this.order.filter(x => x===id).length + 1)
        }

        // Add item to the order list
        this.order.push(id)
    }

    // Remove an item from the order list
    removeItem(element){
        // Gets the id of the item to remove
        // Button id example:
        //  itemgrid-<item>
        var itemId = element.id.split('-')[1];

        // Remove the item from the order list
        this.order.splice(this.order.indexOf(itemId), 1);

        // If there is now no items of that id left
        if (this.order.filter(x => x===itemId).length === 0){
            // We need to remove the button

            element.parentNode.removeChild(element);
        }

        // If there are items of that id left
        else if (this.order.filter(x => x===itemId).length >= 0) {
            // Reduce the count of the button (visual only)

            // Set the text of the button to:
            //  <item-name> x <item-amount>
            element.innerText = element.innerText.split(' x ')[0] + ' x ' + this.order.filter(x => x===itemId).length
        }
    }

    // Send the order to the backend for saving
    // Called by the save button
    saveOrder(){

        // If the current order is being edited
        if (this.editOrNew === 'edit'){

            // Send the request
            $.ajax({
                url: '/orders/edit',
                data: {
                    'items': this.order.toString(), // The order list in a string format (arrays don't seem to work with jQuery and Flask)
                    'id': this.editOrder            // The id of the order is the currently edited order id
                }
            })
        }

        // If the current order is a new order
        else if (this.editOrNew === 'new'){

            // Send the request
            $.ajax({
                url: '/orders/new',
                data: {
                    'items': this.order.toString(), // The order list in a string format (arrays don't seem to work with jQuery and Flask)
                    'table': this.tableNum          // Send the table number as well
                }
            })
        }
    }
}


// Set up a manager with the correct divs
var manager = new Manager(
    document.getElementById('option-page'),
    document.getElementById('create-order'),
    document.getElementById('orders-page'),
    document.getElementById('choose-table')
);

// Set the initial state of the manager
manager.goToMain();
