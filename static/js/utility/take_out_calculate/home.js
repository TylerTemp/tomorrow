$(function() {

  $('form').submit(function (event) {
    event.preventDefault();
    var $form = $(this);
    var $fieldset = $form.find('fieldset');
    var $submit = $form.find('button[type="submit"]');
    var values = {};

    $.each($form.serializeArray(), function (_, field) {
      values[field.name] = parseFloat(field.value);
    });

    if ($.isEmptyObject(values)) {
      console.log('Unexpected empty sumbit');
      return false;
    }

    $submit.button('loading');
    $fieldset.prop('disabled', true);

    var result = values['p'] * values['t'] * values['v'] / values['s'];
    console.log(result);
    $calcint = $('#caculation');
    $bar = $calcint.find('.am-progress-bar');
    $result = $('#result');
    $result_num = $('#result-num');

    $calcint.show();
    $result_num.hide();
    $bar.css('width', '0%');

    setTimeout(function(){ $bar.css('width', '20%'); }, 100);
    setTimeout(function(){ $bar.css('width', '40%'); }, 300);
    setTimeout(function(){ $bar.css('width', '70%'); }, 600);
    setTimeout(function(){ $bar.css('width', '80%'); }, 800);
    setTimeout(function()
    {
      $bar.css('width', '100%');

    }, 1000);

    setTimeout(function(){
      $calcint.hide();
      $result.show();
      $result_num.html(result).show();
      $submit.button('reset');
      $fieldset.prop('disabled', false);
    }, 1600);

  });

});