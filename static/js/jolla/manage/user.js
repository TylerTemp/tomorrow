$(function(){
  // <textarea auto-adjust>
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

  $('.am-collapse').on('opened.collapse.amui', function(event)
  {
    $(this).find('textarea').each(function(index, elem)
    {
      adjust_height(elem);
    });
  });

  // </textarea auto-adjust>

  // <switch avatar>
  var photo_component_switch = function($photo_component)
  {
    var $input = $photo_component.find('input');
    var this_type = $input.prop('type');
    var switch_to = 'file';
    var switch_icon = 'am-icon-file-image-o';
    if (this_type == 'file')
    {
      switch_to = 'text';
      switch_icon = 'am-icon-link';
    }
    $input.prop('type', switch_to);
    $photo_component.find('i')
        .removeClass('am-icon-file-image-o am-icon-link')
        .addClass(switch_icon);
  };

  $('.photo-component').each(function(index, elem)
  {
    var $component = $(elem);
    $component.find('button').click(function(event)
    {
      event.preventDefault();
      photo_component_switch($component);
    });
  });
  // </switch avatar>

  // <delete>
  $('button[data-role="delete"]').each(function(index, elem)
  {
    $(elem).click(function(event)
    {
      console.log('delete clicked');
      event.preventDefault();
      var $form = $(this).closest('form');
      var $action = $form.find('[name="action"]');
      $action.val('delete');
      $form.submit()
    })
  });

  var delete_handler = function($form, ajax)
  {
    var $action = $form.find('[name="action"]');
    ajax
      .done(function(){ $form.hide(300, function(){ $form.remove(); }) })
      .always(function()
      {
        $action.val('');
      });
  }
  // </delete>

  // <submit>
  $('button[type="submit"]').each(function(index, elem)
  {
    $(elem).click(function(event)
    {
      console.log('submit clicked');
      event.preventDefault();
      var $form = $(this).closest('form');
      $form.find('[name="action"]').val('');
      $form.submit();
    });
  });

  var submit_handler = function($form, ajax)
  {
    ajax.done(function(data, textStatus, jqXHR)
    {
      console.log(data);
      $form.find('input[name="name"]').val(data.name || '');
      $form.find('input[name="email"]').val(data.email || '');
      $form.find('select[name="group"]').val(data.type);
      if (data.photo)
      {
        $form.find('img.avatar').prop('src', data.photo);
        var $input = $form.find('.photo-component').find('input[type="text"]');
        if (!$input.length)
          photo_component_switch($photo_component);
        $input = $form.find('.photo-component').find('input[type="text"]');
        $input.val(data.photo);
      }
      $form.find('select[name="home"]').val(data.home || '');
      $form.find('[name="zh-intro"]').val(data.zh_intro || '');
      $form.find('[name="zh-donate"]').val(data.zh_donate || '');
      $form.find('[name="en-intro"]').val(data.en_intro || '');
      $form.find('[name="en-donate"]').val(data.en_donate || '');
      $('<div class="am-alert am-alert-success" data-am-alert><button type="button" class="am-close">&times;</button><p>' +
          _('Done') +
        '</p></div>').appendTo($form.find('.am-panel-bd'));
    });
  }
  // </submit>

  // <form>
  $('form').each(function(index, elem)
  {
    $(elem).submit(function(event)
    {
      event.preventDefault();
      var $form = $(this);

      var $fieldset = $form.find('fieldset');
      var values = new FormData($form[0]);
      var $file_fileds = $form.find('input[type="file"]');
      if ($file_fileds[0])
        $.each($file_fileds[0].files, function(i, file) {
         values.append('file-' + i, file);
        });

      var $submit;
      if (values.get('action') == 'delete')
        $submit = $form.find('button[data-role="delete"]');
      else
        $submit = $form.find('button[type="submit"]');

      $submit.button('loading');
      $fieldset.prop('disabled', true);
      $form.find('.am-alert').hide(300, function(){ $(this).remove() });
      var ajax = $.ajax(
        settings={
          data: values,
          type: 'post',
          processData: false,
          contentType: false,
          beforeSend: function(jqXHR, settings)
          {
            jqXHR.setRequestHeader('X-Xsrftoken', $.AMUI.utils.cookie.get('_xsrf'));
          }
       }
      ).fail(function(jqXHR, textStatus, errorThrown)
      {
        var msg;
        var result = jqXHR.responseJSON;
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
            _('Sorry, a server error occured, please refresh and retry') +
            ' (' + jqXHR.status + ': ' + errorThrown + ')'
          );
       $('<div class="am-alert am-alert-warning" data-am-alert><button type="button" class="am-close">&times;</button><p>' +
           msg +
         '</p></div>').appendTo($form.find('.am-panel-bd'));
      }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
      {
        $submit.button('reset');
        $fieldset.prop('disabled',false);
      });

      if (values.get('action') == 'delete')
        delete_handler($form, ajax);
      else
        submit_handler($form, ajax);
    });
  })
  // </form>
});