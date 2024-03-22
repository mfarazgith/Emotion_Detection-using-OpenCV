document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('openNewTab').addEventListener('click', function() {
      chrome.tabs.create({ url: 'http://127.0.0.1:5000' });
    });
  });
  