
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
    _boolToDisplay(bool){
        if (bool === false){
            return 'none'
        }
        else if (bool === true){
            return 'block'
        }
    }

    // Private Method
    _goTo(main, menu, list, table){
        this.main.style.display = this._boolToDisplay(main);
        this.menu.style.display = this._boolToDisplay(menu);
        this.orderList.style.display = this._boolToDisplay(list);
        this.table.style.display = this._boolToDisplay(table);
    }

    _populateOrderList(){
        $.ajax({
            url: 'orders/get/all',
            success: function (data){
                let list = document.getElementById("orders-page orders-grid");
                list.innerHTML = '';

                data.forEach(function (item, index) {
                    let newItem = document.createElement('button');
                    newItem.className = 'orders-page order-button';
                    newItem.id = 'order-' + item[0];
                    newItem.onclick = function () {manager.goToEditOrder(item)};
                    newItem.appendChild(document.createTextNode(item[3]));
                    list.appendChild(newItem)
                })
            }
        });
    }

    goToMain(){
        this._goTo(true, false, false, false);
    }

    goToChooseTable(){
        this._goTo(false, false, false, true);
    }

    goToNewOrder(id){
        this.tableNum = id.split('-')[1];
        this.editOrNew = 'new';

        document.getElementById('create-order order-title').innerText = 'New Order For Table ' + this.tableNum;

        this.order = [];
        document.getElementById('create-order item-grid').innerHTML = '';

        this._goTo(false, true, false, false);
    }

    goToEditOrder(item){
        this.tableNum = item[1];
        this.editOrder = item[0];
        this.editOrNew = 'edit';
        document.getElementById('create-order order-title').innerText = 'Editing Order For Table ' + this.tableNum;

        this.order = [];
        document.getElementById('create-order item-grid').innerHTML = '';

        item[2].forEach(function (order_item) {
            var itemId = order_item[0];
            var itemName = order_item[1];

            this._addItem(itemId, itemName);
        }.bind(this));

        console.log(this.order);
        this._goTo(false, true, false, false);
    }

    goToOrderList(){
        this._populateOrderList();

        this._goTo(false, false, true, false);
    }

    addItem(element){
        var itemId = element.id.split('&')[0].split('-')[1];
        var itemName = element.id.split('&')[1].split('-')[1];

        this._addItem(itemId, itemName)
    }

    _addItem(id, name){
        var list = document.getElementById('create-order item-grid');

        if (this.order.includes(id) === false){
            var newItem = document.createElement('button');
            newItem.className = 'create-order item-grid-button';
            newItem.id = 'itemgrid-' + id;
            newItem.onclick = function () {manager.removeItem(this)};
            newItem.appendChild(document.createTextNode(name + ' x 1'));
            list.appendChild(newItem)
        }
        else if (this.order.includes(id) === true){
            var existingItem = document.getElementById('itemgrid-' + id);

            existingItem.innerText = name + ' x ' + (this.order.filter(x => x===id).length + 1)
        }
        this.order.push(id)
    }


    removeItem(element){
        var itemId = element.id.split('-')[1];

        var existingItem = document.getElementById('itemgrid-' + itemId);

        this.order.splice(this.order.indexOf(itemId), 1);

        if (this.order.filter(x => x===itemId).length === 0){
            existingItem.parentNode.removeChild(existingItem);
        }
        else if (this.order.filter(x => x===itemId).length >= 0) {
            var amount = parseInt(existingItem.innerText.split(' x ')[1]) - 1;
            existingItem.innerText = existingItem.innerText.split(' x ')[0] + ' x ' + amount
        }
    }

    saveOrder(){
        if (this.editOrNew === 'edit'){
            console.log('edit');
            $.ajax({
                url: '/orders/edit',
                data: {
                    'items': this.order.toString(),
                    'id': this.editOrder
                }
            })
        }
        else if (this.editOrNew === 'new'){
            console.log('new');
            $.ajax({
                url: '/orders/new',
                data: {
                    'items': this.order.toString(),
                    'table': this.tableNum
                }
            })
        }


    }

}


var manager = new Manager(
    document.getElementById('option-page'),
    document.getElementById('create-order'),
    document.getElementById('orders-page'),
    document.getElementById('choose-table')
);

manager.goToMain();

