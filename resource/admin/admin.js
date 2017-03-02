$(function() {
  var src = document.getElementById('src');
  if(src) {
    var myCodeMirror = CodeMirror.fromTextArea(src, {
      lineNumbers: true,
      mode: "text/x-yaml"
    });
  }

  $('#insert-default-src').click(function(ev) {
    ev.preventDefault();
    var defaults = $('#default-srcs').html();
    var defaults = JSON.parse(defaults);
    var template = $('select[name=template]').val();
    var src = defaults[template];
    myCodeMirror.setValue(src);
  });
});
