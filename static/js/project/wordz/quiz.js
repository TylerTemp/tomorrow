$(function ()
{

  var TagSelector = function($table_body){
    this.tags = {};
    this.shown_id = [];
    this.id_to_words = {};
    this.$table_body = $table_body;
  };

  TagSelector.prototype.tags;
  TagSelector.prototype.shown_id;
  TagSelector.prototype.id_to_words;
  TagSelector.$table_body;

  TagSelector.prototype.load = function(tag, ok_callback, fail_callback, always_callback)
  {
    var self = this;
    if (this.tags[tag] !== undefined)
    {
      ok_callback(this.tags[tag]);
      if (always_callback)
        always_callback();
    }

    console.log('from server: ' + tag);
    var ajax = $.ajax(settings={
      data: {'tag': tag},
      type: 'get'
    }).done(function(data, textStatus, jqXHR)
    {
      var result = $.parseJSON(data);
      self.tags[tag] = result;
      self.add_words(result);
      self.render_words(result);
      ok_callback(result);
    });
    if (fail_callback)
      ajax.fail(fail_callback);
    if (always_callback)
      ajax.always(always_callback);
  };

  TagSelector.prototype.add_words = function(words)
  {
    for (var index in words)
    {
      var word_obj = words[index];
      this.id_to_words[word_obj.id] = word_obj;
    }
  };

  TagSelector.prototype.render_words = function(words)
  {
    var shown = this.shown_id;
    for (var index in words)
    {
      var word_obj = words[index];
      var id = word_obj.id;
      if (shown.indexOf(id) !== -1)
        continue;
      this.insert(word_obj);
      this.shown_id.push(word_obj.id);
    }
  };

  TagSelector.prototype.insert = function(word)
  {
    var $tbody = this.$table_body;
    var meanings = [];
    for (var type in word.meaning)
    {
      var mean = word.meaning[type].join('; ');
      meanings.push('&lt;' + type + '&gt; ' + mean);
    }


    var tags = [];
    for (var index in word.tag)
    {
      var $badge = '<span class="am-badge">' + word.tag[index] + '</span>';
      tags.push($badge);
    }
    var $html = $(
      '<tr>'+
        '<td>' +
          '<label class="am-checkbox">' +
            '<input type="checkbox" data-am-ucheck data-id="' + word.id + '">' +
          '</label>' +
        '</td>' +
        '<td>' + word.spell.join(' / ') + '</td>' +
        '<td>' + meanings.join('<br/>') + '</td>' +
        '<td>' + (word.pronounce? ('[' + word.pronounce + ']'): '<span class="am-icon-times"></span>') + '</td>' +
        '<td>' + tags.join(' ') + '</td>' +
      '</tr>'
    );

    $html.find('input[type="checkbox"]').uCheck('check');

    $html.hide();
    $tbody.prepend($html);
    $html.show(100);
  };


  var tag_selector = new TagSelector($('#word-list tbody'));
  var $confirm_btn = $('#tag-confirm');

  var $tag_select = $('#select-tags');
  $tag_select.select2({
    placeholder: _("Select Tags"),
    allowClear: true
  });
  $tag_select.on('select2:select', function(name, event)
  {
    var tag = name.params.data.text;
    console.log(tag);
    $confirm_btn.button('loading');
    tag_selector.load(
        tag,
        function(result){console.log(result)},
        function(jqXHR, textStatus, errorThrown){ alert('' + jqXHR.status + ': ' + errorThrown); },
        function(){ $confirm_btn.button('reset'); });
  });

});