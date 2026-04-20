<script context="module">
    export function waitForToken(tokenName) {
        return new Promise((resolve) => {
            const check = () => {
                const token = sessionStorage.getItem(tokenName);
                if (token) {
                    resolve(token);
                } else {
                    setTimeout(check, 50);
                }
            };
            check();
        });
    }
</script>