$(function()
{

  var substringMatcher = function(strs) {
    return function findMatches(q, cb) {
      var matches, substringRegex;

      // an array that will be populated with substring matches
      matches = [];

      // regex used to determine if a string contains the substring `q`
      substrRegex = new RegExp(q, 'i');

      // iterate through the pool of strings and for any string that
      // contains the substring `q`, add it to the `matches` array
      $.each(strs, function(i, str) {
        if (substrRegex.test(str)) {
          matches.push(str);
        }
      });

      cb(matches);
    };
  };

var states = [
  'statuses/public_timeline',
  'statuses/friends_timeline',
  'statuses/home_timeline',
  'statuses/friends_timeline/ids',
  'statuses/user_timeline',
  'statuses/user_timeline/ids',
  'statuses/timeline_batch',
  'statuses/repost_timeline',
  'statuses/repost_timeline/ids',
  'statuses/mentions',
  'statuses/mentions/ids',
  'statuses/bilateral_timeline',
  'statuses/show',
  'statuses/show_batch',
  'statuses/querymid',
  'statuses/queryid',
  'statuses/count',
  'statuses/go',
  'emotions',
  'statuses/repost',
  'statuses/destroy',
  'statuses/update',
  'statuses/upload',
  'statuses/upload_url_text',
  'statuses/filter/create',
  'statuses/mentions/shield',
  'comments/show',
  'comments/by_me',
  'comments/to_me',
  'comments/timeline',
  'comments/mentions',
  'comments/show_batch',
  'comments/create',
  'comments/destroy',
  'comments/destroy_batch',
  'comments/reply',
  'users/show',
  'users/domain_show',
  'users/counts',
  'friendships/friends',
  'friendships/friends/in_common',
  'friendships/friends/bilateral',
  'friendships/friends/bilateral/ids',
  'friendships/friends/ids',
  'friendships/followers',
  'friendships/followers/ids',
  'friendships/followers/active',
  'friendships/friends_chain/followers',
  'friendships/show',
  'friendships/create',
  'friendships/destroy',
  'account/profile/school_list',
  'account/rate_limit_status',
  'account/profile/email',
  'account/get_uid',
  'favorites',
  'favorites/ids',
  'favorites/show',
  'favorites/by_tags',
  'favorites/tags',
  'favorites/by_tags/ids',
  'favorites/create',
  'favorites/destroy',
  'favorites/destroy_batch',
  'favorites/tags/update',
  'favorites/tags/update_batch',
  'favorites/tags/destroy_batch',
  'search/suggestions/users',
  'search/suggestions/schools',
  'search/suggestions/companies',
  'search/suggestions/apps',
  'search/suggestions/at_users',
  'search/topics',
  'remind/unread_count',
  'remind/set_count',
  'short_url/shorten',
  'short_url/expand',
  'short_url/share/counts',
  'short_url/share/statuses',
  'short_url/comment/counts',
  'short_url/comment/comments',
  'common/code_to_location',
  'common/get_city',
  'common/get_province',
  'common/get_country',
  'common/get_timezone',
  'place/public_timeline',
  'place/friends_timeline',
  'place/user_timeline',
  'place/poi_timeline',
  'place/nearby_timeline',
  'place/statuses/show',
  'place/users/show',
  'place/users/checkins',
  'place/users/photos',
  'place/users/tips',
  'place/users/todos',
  'place/pois/show',
  'place/pois/users',
  'place/pois/tips',
  'place/pois/photos',
  'place/pois/search',
  'place/pois/category',
  'place/nearby/pois',
  'place/nearby/users',
  'place/nearby/photos',
  'place/nearby_users/list',
  'place/pois/create',
  'place/pois/add_checkin',
  'place/pois/add_photo',
  'place/pois/add_tip',
  'place/pois/add_todo',
  'place/nearby_users/create',
  'place/nearby_users/destroy',
  'location/base/get_map_image',
  'location/geo/ip_to_geo',
  'location/geo/address_to_geo',
  'location/geo/geo_to_address',
  'location/geo/gps_to_offset',
  'location/geo/is_domestic',
  'location/pois/search/by_location',
  'location/pois/search/by_geo',
  'location/pois/search/by_area',
  'location/pois/show_batch',
  'location/pois/add',
  'location/mobile/get_location',
  'location/line/drive_route',
  'location/line/bus_route',
  'location/line/bus_line',
  'location/line/bus_station',
  'location/citycode',
  'location/citycode_bus',
  'location/category',
  'location/error2',
  'oauth2/authorize',
  'oauth2/access_token',
  'oauth2/get_token_info',
  'oauth2/get_oauth2_token',
  'OAuth2/revokeoauth2'
];

  var $method = $('#func');
  $method.typeahead({
    hint: true,
    highlight: true,
    minLength: 1
  },
  {
    name: 'method',
    source: substringMatcher(states)
  });

  var bind_row = function($ele)
  {
    $delete = $ele.find('[data-role="delete"]');
    $delete.click(function(event)
    {
      event.preventDefault();
      $ele.remove();
    });
    $select = $ele.find('select');
    var $parent = $select.closest('td');
    var $next = $parent.next();
    $select.on('change', function(event)
    {
      var choose = $(this).val();
      console.log(choose);
      if (choose == 'binary')
      {
        $next.html('<input type="file" />');
        bind_file_input($next.find('input[type="file"]'));
      }
      else
        $next.html('<input type="text" />');
    });
  };

  var bind_file_input = function($input)
  {
    $input.on('change', function(event)
    {
      console.log('changed');
      if (this.type === 'file' && this.files && this.files.length > 0)
      {
        var file_info = event.target.files[0];
        console.log(file_info);
        var file_type = file_info.type;
        var main_type = file_type.split('/')[0];
        var sub_type = file_type.split('/')[1];
        var file_name = file_info.name;
        var $currect = $(
          '<div class="am-progress am-progress-striped am-progress-xl am-active">' +
            '<div class="am-progress-bar am-progress-bar-secondary"  style="width: 5%">' +
            '</div>' +
          '</div>');
        $input.replaceWith($currect);
        readFileIntoDataurl(file_info)
        .fail(function(e, name, size, type)
        {
          var $error = $(
              '<div class="am-alert am-alert-warning" data-am-alert>' +
                '<button type="button" class="am-close">&times;</button>' +
                '<p>' + 'Failed to load file ' + name + '</p>' +
              '</div>');
          $current.replaceWith($error);
          $error.on('closed.alert.amui', function()
          {
            var $current = $('<input type="file" />');
            $error.replaceWith($current);
            bind_file_input($current);
          });
        }).progress(function(loaded, total, name, size, type)
        {
          var process = Math.round(loaded * 100 / total);
          $currect.find('am-progress-bar').css('width', process.toString() + '%');
        }).done(function(dataUrl, name, size, type)
        {
          $currect.find('am-progress-bar').css('width', '100%');
          $new = $('<div><input class="data-value"/><button class="am-btn am-icon-trash"></button></div>');
          $new.find('input').val(dataUrl);
          $new.find('button').click(function(event)
          {
            event.preventDefault();
            var $current = $('<input type="file" />');
            $new.replaceWith($current);
            bind_file_input($current);
          });
          $currect.replaceWith($new);
          $currect = $new;
        });
      }
    });
  };

  $('#arguments').find('tr').each(function(index, ele)
  {
    bind_row($(ele));
  });

  $('[data-role="add"]').click(function(event)
  {
    event.preventDefault();
    var $result = $(
      '<tr>' +
        '<td><input type="text"></td>' +
        '<td>' +
          '<select>' +
            '<option value="string" selected="selected">string</option>' +
            '<option value="int">int</option>' +
            '<option value="binary">binary</option>' +
          '</select>' +
        '</td>' +
        '<td><input type="text"></td>' +
        '<td><button class="am-btn am-icon-times" data-role="delete"></button></td>' +
      '</tr>');
    $result.appendTo($('#arguments'));
    bind_row($result);
  });

  $('form').submit(function(event)
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
    console.log(values);

    var args = [];
    $form.find('tr').each(function(index, ele)
    {
      var $row = $(ele);
      var $cols = $row.find('td');
      var name = $cols.eq(0).find('input').val();
      if (!name)
        return ;
      var type = $cols.eq(1).find('select').val();
      var $value = $cols.eq(2).find('input');
      if (!$value.length)
        return ;
      var value = $value.val();
      if (!value)
        return ;
      console.log(name, type, (type == 'binary'? '[binary]': value));
      args.push({'name': name, 'type': type, 'value': value});
    });

    values['arguments'] = JSON.stringify(args);
    console.log(values['arguments']);

    $fieldset.prop('disabled', true);
    $submit.button('loading');
    $('#result').html('<i class="am-icon-spinner am-icon-pulse am-text-lg"></i>');

    $.ajax(settings={
      data: values,
      type: 'post'
    }).done(function(data, textStatus, jqXHR)
    {
      console.log(data);
      $('#result').html('<pre>' + data + '</pre>');
    }
    ).fail(function(jqXHR, textStatus, errorThrown)
    {
      console.log(jqXHR.responseText, textStatus, errorThrown);
      var data = jqXHR.responseText;
      var msg = _('Sorry, a server error occured, please refresh and retry');
      var error = jqXHR.status + ': ' + errorThrown;
      try
      {
        result = $.parseJSON(data);
        error = result.error;
      }
      catch (e)
      {}
      msg += (' (' + error + ')');

      $('#result').html(
        '<div class="am-alert am-alert-danger" data-am-alert>' +
          '<button type="button" class="am-close">&times;</button>' +
          '<p>' + msg + '</p>' +
        '</div>'
      );
    }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
    {
      $fieldset.prop('disabled', false);
      $submit.button('reset');
    });
  });
});