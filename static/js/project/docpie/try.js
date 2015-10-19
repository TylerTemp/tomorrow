$(function(evt)
{
  // <auto-textarea-height>
  var adjust_height = function(element)
  {
    $(element).css({'height':'auto','overflow-y':'hidden'})
              .height(element.scrollHeight - 10);
  };

  $('textarea').each(function()
  {
    adjust_height(this);
  }).on('input', function()
  {
    adjust_height(this);
  });
  // </auto-textarea-height>

  // <monitor-config>
    // <element>
  var $config = $('#config');
  var $help = $('input[name="help"]');
  var $version = $('input[name="version"]');
  var $stdopt = $('input[name="stdopt"]');
  var $attachopt = $('input[name="attachopt"]');
  var $attachvalue = $('input[name="attachvalue"]');
  var $auto2dashes = $('input[name="auto2dashes"]');
  var $name = $('input[name="name"]');
  var $file_name = $('[data-role="file-name"]');
  var $case_sensitive = $('input[name="case_sensitive"]');
  var $optionsfirst = $('input[name="optionsfirst"]');
  var $appearedonly = $('input[name="appearedonly"]');
    // </element>
    // <update-ui>
  var refresh = function()
  {
    var all_elements = [];
    order = ['help', 'version', 'stdopt', 'attachopt', 'attachvalue',
             'auto2dashes', 'name', 'case_sensitive', 'optionsfirst',
             'appearedonly'];
    for (var index in order)
    {
      var arg_name = order[index];
      var arg_value = config_status[arg_name];
      console.log('%s = %s', arg_name, arg_value);
      if (arg_value === undefined)
        continue;
      switch (arg_value) {
        case ('true'):
        case (true):
            arg_value = 'True';
            break;
        case ('false'):
        case (false):
            arg_value = 'False';
            break;
      }
      all_elements.push(', ' + arg_name + '=' + arg_value);
    }
    console.log(all_elements.join(''));
    $config.html(all_elements.join(''));
  };

  var set_value = function(name, value, default_)
  {
    console.log('%s = %s / %s', name, value, default_);
    if (value === default_)
      delete config_status[name];
    else
      config_status[name] = value;
    refresh();
  };
    // </update-ui>
    // <bind>
  $help.change(function(event)
  {
    var value = $(this).filter(':checked').val();
    set_value('help', value, 'true');
  });
  $version.blur(function(event)
  {
    var value = $(this).val();
    if (value)
      value = "'" + value.replace(/'/g, "\\'") + "'";
    else
      value = undefined;
    set_value('version', value);
  });
  $stdopt.change(function(event)
  {
    var value = $(this).filter(':checked').val();
    set_value('stdopt', value, 'true');
  });
  $attachopt.change(function(event)
  {
    var value = $(this).filter(':checked').val();
    set_value('attachopt', value, 'true');
  });
  $attachvalue.change(function(event)
  {
    var value = $(this).filter(':checked').val();
    set_value('attachvalue', value, 'true');
  });
  $auto2dashes.change(function(event)
  {
    var value = $(this).filter(':checked').val();
    set_value('auto2dashes', value, 'true');
  });
  $name.blur(function(event)
  {
    var value = $(this).val();
    if (value)
    {
      $file_name.html(value);
      value = "'" + value.replace(/'/g, "\\'") + "'";
    }
    else
    {
      value = undefined;
    }
    set_value('name', value);
  });
  $case_sensitive.change(function(event)
  {
    var value = $(this).filter(':checked').val();
    set_value('case_sensitive', value, 'false');
  });
  $optionsfirst.change(function(event)
  {
    var value = $(this).filter(':checked').val();
    set_value('optionsfirst', value, 'false');
  });
  $appearedonly.change(function(event)
  {
    var value = $(this).filter(':checked').val();
    set_value('appearedonly', value, 'false');
  });
    // </bind>
  // </monitor-config>
  // <form>
  $('form').submit(function(event)
  {
    event.preventDefault();
    var $form = $(this);
    var $button = $form.find('button[type="submit"]');
    var $fieldset = $form.find('fieldset');
    var $code = $form.find('pre code');
    var $end_dollar = $form.find('[data-role="end_dollar"]');

    var values = {};
    $.each($form.serializeArray(), function(i, field)
    {
      values[field.name] = field.value;
    });

    $code.html(
      '<i class="am-icon-spinner am-icon-pulse am-text-xxxl am-center"></i>'
    );

    $button.button('loading');
    $fieldset.prop('disabled', true);
    $end_dollar.hide();

    $.ajax(
      location.pathname,
      settings={
        data: values,
        type: 'get'
      }
    ).done(function(data, textStatus, jqXHR)
    {
      var obj = $.parseJSON(data);
      $code.text(obj.output);
    }).fail(function(jqXHR, textStatus, errorThrown)
    {
      var msg = _("Sorry, a server error occured, please refresh and retry") +
                " ({0}: {1})".format(jqXHR.status, errorThrown);
      $code.text(msg);
    }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
    {
      $button.button('reset');
      $fieldset.prop('disabled', false);
      $end_dollar.show();
    })
  });
  // </form>
});