function goto(href) {
  var $page = $('.page[data-path="' + href + '"]')
  var title = $page.data('title')
  var baseUrl = window.BASE_URL
  var stripped = baseUrl.substring(0, baseUrl.length - 1)
  window.history.pushState("", title, (stripped + href))
  handleLocation()
}

function handleLocation() {
  var path = window.document.location.pathname
  var href = '/' + path.replace(new RegExp('^' + window.BASE_URL), "")
  var $page = $('.page[data-path="' + href + '"]')
  var title = $page.data('title')
  $('.page').hide()
  $page.show()
  document.title = title + ' - ' + window.BASE_TITLE
}

window.onpopstate = function(event) {
  handleLocation()
}

$(function() {
  window.BASE_URL = $('body').data('base')
  window.BASE_TITLE = $('body').data('title')

  $('.nav-link').click(function(ev) {
    ev.preventDefault()
    var $target = $(ev.currentTarget)
    var href = $target.attr('href')
    goto(href)
  })

  handleLocation()
})
