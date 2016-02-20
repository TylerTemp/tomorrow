$(function()
{
  var $form = $('form');

  var edit_handler = function(event)
  {
    event.preventDefault();
    var $edit = $(this);
    var $container = $edit.closest('tr');
    var $td = $container.find('td');
    var source = $td.eq(0).text();
    var target = $td.eq(1).text();
    var checked = $td.find('span').hasClass('am-icon-check-square-o');
    console.log(source, target, checked);
    $form.find('input[name="source"]').val(source);
    $form.find('input[name="target"]').val(target);
    $form.find('input[name="permanent"]').prop("checked", checked);
    $('html,body').animate(
    {
       scrollTop: $form.offset().top
    });
  };

  // <edit>
  $('table').find('button').each(function(index, elem)
  {
    var $edit = $(elem);
    $edit.click(edit_handler);
  });
  // </edit>

  // <save>
  $form.find('[type="submit"]').click(function(event)
  {
    event.preventDefault();
    $form.find('[name="action"]').val('');
    $form.submit();
  });

  var save_handler = function($form, ajax)
  {
    ajax.done(function(data, textStatus, jqXHR)
    {
      console.log(data);
      $form.find('[name="source"]').val(data.source);
      $form.find('[name="target"]').val(data.target);
      $form.find('[name="permanent"]').prop("checked", data.permanent);
      var found = false;
      var $container;
      $('tr').each(function(index, elem)
      {
        $container = $(elem);
        var $source = $container.find('td:nth-child(1)');
        if ($source.text() == data.source)
        {
          $container.find('td:nth-child(2)').text(data.target);
          $container.find('span')
              .removeClass('am-icon-check-square-o')
              .removeClass('am-icon-square-o')
              .addClass(data.permanent && 'am-icon-check-square-o' || 'am-icon-square-o');
          found = true;
          return false;
        }
      });

      if (!found)
      {
        $container = $(
          '<tr>' +
            '<td>' + data.source + '</td>' +
            '<td>' + data.target + '</td>' +
            '<td><span class="am-icon-' + (data.permanent && 'check-square-o' || 'square-o') + '"></span></td>' +
            '<td><button class="am-btn am-btn-default am-btn-sm am-icon-edit" title="edit"></button></td>' +
          '</tr>'
        ).appendTo($('table'));
      }

      $('html,body').animate(
      {
         scrollTop: $container.offset().top
      });

    });
  };
  // </save>

  // <delete>
  $form.find('[data-role="delete"]').click(function(event)
  {
    event.preventDefault();
    $form.find('[name="action"]').val('delete');
    $form.submit();
  });

  var delete_handler = function($form, ajax)
  {
    ajax.done(function(data, textStatus, jqXHR)
    {
      $('tr').each(function(index, elem)
      {
        $container = $(elem);
        var $source = $container.find('td:nth-child(1)');
        if ($source.text() == data.source)
        {
          $('html,body').animate(
          {
            scrollTop: $container.offset().top
          },
          {
            complete: function()
            {
              $container.hide(300, function()
              {
                $container.remove();
              });
            }
          });
          return false;
        }
      });
    }).always(function()
    {
      $form.find('[name="action"]').val('');
    });
  };
  // </delete>

  // <submit>
  $form.submit(function(event)
  {
    event.preventDefault();
    var $form = $(this);
    var $fieldset = $form.find('fieldset');
    var $submit = $form.find('button[type="submit"]');
    var values = {};
    $.each($form.serializeArray(), function(_, field)
    {
        values[field.name] = field.value;
    });
    if ($.isEmptyObject(values))
    {
      console.log('Unexpected empty submit');
      return false;
    }

    $submit.button('loading');
    $fieldset.prop('disabled', true);
    $form.find('.am-alert').remove();
    var ajax = $.ajax(
      settings={
        data: values,
        type: 'post',
        beforeSend: function(jqXHR, settings)
        {
          jqXHR.setRequestHeader('X-Xsrftoken', $.AMUI.utils.cookie.get('_xsrf'));
        }
      }
    ).fail(function(jqXHR, textStatus, errorThrown)
    {
      var result = jqXHR.responseJSON;
      var msg;
      if (result)
        msg = result.message;
      if (!msg)
      {
        try
        {
          result = $.parseJSON(jqXHR.responseText);
          if (result.message)
            msg = result.message;
        }
        catch (e) {}
      }
      if (!msg)
       msg = (
         'Sorry, a server error occured, please refresh and retry' +
         ' (' + jqXHR.status + ': ' + errorThrown + ')'
       );
      $('<div class="am-alert am-alert-danger" data-am-alert>' +
          '<button type="button" class="am-close">&times;</button>' +
          '<p>' + msg + '</p>' +
        '</div>').appendTo($form);
    }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
    {
      $submit.button('reset');
      $fieldset.prop('disabled',false);
    });

    if (values.action == 'delete')
        return delete_handler($form, ajax);
    return save_handler($form, ajax);
  });
  // </submit>
});