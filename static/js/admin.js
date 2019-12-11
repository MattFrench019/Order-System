
function _addLine(line){
    const display = document.getElementById('admin-display');
    display.innerText = display.innerText + line + '\n';

    display.scrollTop = display.scrollHeight;
}

function sendCmd(){
    const entry = document.getElementById('admin-entry');

    let request = $.ajax({
        url: '/admin/backend',
        data: {'cmd': entry.value},
    });

    request.done(function (data) {
        _addLine(data)
    });

    request.fail(function () {
        _addLine('Connection Error, Server may be restarting!')
    })
}