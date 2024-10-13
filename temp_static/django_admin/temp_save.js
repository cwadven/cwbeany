document.addEventListener('DOMContentLoaded', function () {
    function sendTemporarySave(queue_name, value) {
        const data = {
            queue_name: queue_name,
            value: value
        };

        fetch('/post/temporary-save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(data)
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log('Success:', data);
            })
            .catch((error) => {
                console.error('Error:', error);
            });
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function getCurrentUrl() {
        return window.location.href;
    }

    const url = getCurrentUrl();
    const urlParts = url.split('/');
    const postId = urlParts[urlParts.length - 3];
    let queueName;
    if (postId === 'post') {
        queueName = document.querySelector('#user-tools strong').innerHTML;
    } else {
        queueName = `post_${postId}`;
    }

    if (typeof CKEDITOR !== 'undefined') {
        CKEDITOR.on('instanceReady', function (event) {
            const editor = event.editor;
            let debounceTimer;

            function debounce(func, delay) {
                return function(...args) {
                    if (debounceTimer) {
                        clearTimeout(debounceTimer);
                    }
                    debounceTimer = setTimeout(() => {
                        func(...args);
                    }, delay);
                };
            }

            editor.on('change', function () {
                const value = editor.getData();
                debounce(sendTemporarySave, 500)(queueName, value);
            });
        });
    } else {
        console.error('CKEditor is not defined');
    }
});
