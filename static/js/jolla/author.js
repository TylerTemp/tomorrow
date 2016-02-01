$(function(){

  var adjust_height = function(element)
  {
    $(element).css({'height':'auto','overflow-y':'hidden'})
              .height(element.scrollHeight - 10);
  };

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

  var bind_display = function($display)
  {
    var $intro = $display.find('textarea');
    adjust_height($intro[0]);
    $intro.on('input', function()
    {
      adjust_height(this);
    });

    var $photo_component = $display.find('.photo-component');

    $photo_component.find('button').click(function(event)
    {
      event.preventDefault();
      photo_component_switch($photo_component);
    });

    console.log($display.find('form'));

    $display.find('form').submit(function(event)
    {
      event.preventDefault();
      var $form = $(this);
      var $fieldset = $form.find('fieldset');
      var $submit = $form.find('button[type="submit"]');
      var values = new FormData($form[0]);
      var $file_fileds = $form.find('input[type="file"]');
      if ($file_fileds[0])
        $.each($file_fileds[0].files, function(i, file) {
         values.append('file-' + i, file);
        });

      $submit.button('loading');
      $fieldset.prop('disabled', true);
      $form.find('.am-alert').hide(300, function(){ $(this).remove() });
      $.ajax(
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
      ).done(function(data, textStatus, jqXHR)
      {
        console.log(data);
        if (data.photo)
        {
          $display.find('img').prop('src', data.photo);
          var $input = $form.find('.photo-component').find('input[type="text"]');
          if (!$input.length)
            photo_component_switch($photo_component);
          $input = $form.find('.photo-component').find('input[type="text"]');
          $input.val(data.photo);
        }
        $form.find('textarea').val(data.intro || '');

      }).fail(function(jqXHR, textStatus, errorThrown)
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
            'Sorry, a server error occured, please refresh and retry' +
            ' (' + jqXHR.status + ': ' + errorThrown + ')'
          );
       $('<div class="am-alert am-alert-warning" data-am-alert><button type="button" class="am-close">&times;</button><p>' +
           msg +
         '</p></div>').appendTo($form);
      }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
      {
        $submit.button('reset');
        $fieldset.prop('disabled',false);
      });

    });

  };

  $('.am-collapse').on('open.collapse.amui', function(event)
  {
    var $this = $(this);
    if($this.data('loaded'))
      return;

    var id = $this.prop('id');
    var $body = $this.find('.am-panel-bd');

    var name = $this.data('name');
    console.log(name);

    $body.html('<p class="am-text-center am-text-xl"><i class="am-icon-spinner am-icon-pulse"></i> ' + _('Loading...') + '</p>');
    $.ajax(
      settings={
        data: {load: name},
        type: 'get'
      }
    ).done(function(data, textStatus, jqXHR)
    {
      console.log(data);
      $this.data('loaded', 'true');
      var $display = $(
        '<div>' +
          '<div class="am-u-sm-12 am-u-md-3 am-text-center">' +
            '<img src="' + (data.photo || '/static/img/user.jpg') + '" class="am-img-thumbnail am-circle" />' +
          '</div>' +
          '<form class="am-form am-u-sm-12 am-u-md-9"  enctype="multipart/form-data" method="post">' +
            '<legend>' + data.name + '</legend>' +
            '<fieldset>' +

              '<input style="display: none" name="name" value="' + data.name + '" />' +
              '<input style="display: none" name="_xsrf" value="' + $.AMUI.utils.cookie.get('_xsrf') + '" />' +

              '<div class="am-form-group">' +
                '<label for="' + id + 'photo">' + _('Photo') + '</label>' +
                '<div class="am-form-group photo-component">' +
                  '<i class="'+ (data.photo && 'am-icon-link' || 'am-icon-file-image-o') + '"></i>' +
                  // '<input id="' + id + 'photo" type="file" class="am-form-field" name="photo">' +
                  '<input id="' + id + 'photo" type="'+ (data.photo && 'text' || 'file')  + '" class="am-form-field" name="photo" value="' + (data.photo || '') + '">' +
                  '<button class="am-btn"><span class="am-icon-exchange"></span></button>' +
                '</div>' +
              '</div>' +

              '<div class="am-form-group">' +
                '<label for="' + id + 'intro">' + _('Introduction') + '</label>' +
                '<textarea id="' + id + 'intro" name="intro">' + (data.intro || '') + '</textarea>' +
              '</div>' +

              '<div class="am-form-group am-cf">' +
                '<button class="am-btn am-btn-primary am-fr" type="submit" data-am-loading="{spinner: \'refresh\', loadingText: \'\'}">' + _('Submit') + '</button>' +
              '</div>' +

            '</fieldset>' +
          '</form>' +
        '</div>');
      $body.html('');
      $display.appendTo($body);
      bind_display($display);
    }).fail(function(jqXHR, textStatus, errorThrown)
    {
      var msg;
      try
      {
       var result = $.parseJSON(jqXHR.responseText);
       if (result.message)
         msg = result.message;
      }
      catch (e) {}
      if (!msg)
        msg = (
          'Sorry, a server error occured, please refresh and retry' +
          ' (' + jqXHR.status + ': ' + errorThrown + ')'
        );
      var $alert = $(
          '<div class="am-alert am-alert-danger" data-am-alert>' +
            '<button type="button" class="am-close">&times;</button>' +
            '<p>' + msg + '</p>' +
          '</div>');
      $body.html('');
      $alert.appendTo($body);
      $alert.on('close.alert.amui', function(){ $this.collapse('close') });
    });

  });
});