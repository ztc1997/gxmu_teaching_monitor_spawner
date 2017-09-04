function spawn() {
    var state = $('#state');
    var modal1 = $('#modal1');
    var modal1Footer = $('#modal1-footer');

    state.html('正在发送请求');
    modal1Footer.hide();

    modal1.modal('open', {
        dismissible: false
    });

    var formData = $("form").serializeObject();
    var socket = io(window.location.pathname, {reconnection: false});
    socket.on('connect', function () {
        socket.emit('spawn', formData);
        state.html('等待服务器响应');
    });
    socket.on('disconnect', function () {
        state.html('已断开连接');
        modal1Footer.show();
    });
    socket.on('error', function () {
        state.html('连接错误');
        modal1Footer.show();
    });
    socket.on('connect_failed', function () {
        state.html('连接失败');
        modal1Footer.show();
    });
    socket.on('update', function (data) {
        state.html(data);
    });
    socket.on('complete', function () {
        modal1Footer.show();
    });
}