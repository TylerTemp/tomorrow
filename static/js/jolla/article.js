$(function()
{
  if(window.location.hash)
  {
    var hash = window.location.hash; //Puts hash in variable, and removes the # character
    // alert(hash);
    console.log('scroll to ' + hash);
    $('html, body').animate({
      scrollTop: $(hash).offset().top
    }, 2000);
    // hash found
  }
  else {
      // No hash found
  }

});
