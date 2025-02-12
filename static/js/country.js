document.addEventListener("DOMContentLoaded", function () {
    const countrySelect = document.getElementById("country");
    const stateSelect = document.getElementById("state_prefecture");

    // 198カ国リストを動的に読み込む
    fetch("/static/js/countries.json")
        .then(response => response.json())
        .then(countries => {
            countries.forEach(country => {
                const option = document.createElement("option");
                option.value = country.code;
                option.textContent = country.name;
                countrySelect.appendChild(option);
            });

            // 選択状態を復元
            if (countrySelect.dataset.selected) {
                countrySelect.value = countrySelect.dataset.selected;
                countrySelect.dispatchEvent(new Event("change"));
            }
        })
        .catch(error => console.error("国リストの読み込みエラー:", error));

    // 国を変更した際に州/県のリストを更新
    countrySelect.addEventListener("change", function () {
        const selectedCountry = this.value;

        // `states.json` から該当する州/県リストを取得
        fetch("/static/js/states.json")
            .then(response => response.json())
            .then(states => {
                stateSelect.innerHTML = "";
                
                const defaultOption = document.createElement("option");
                defaultOption.value = "";
                defaultOption.textContent = "Choose a state/prefecture...";
                stateSelect.appendChild(defaultOption);

                if (states[selectedCountry]) {
                    states[selectedCountry].forEach(state => {
                        const option = document.createElement("option");
                        option.value = state;
                        option.textContent = state;
                        stateSelect.appendChild(option);
                    });
                }

                // 州/県の選択状態を復元
                if (stateSelect.dataset.selected) {
                    stateSelect.value = stateSelect.dataset.selected;
                }
            })
            .catch(error => console.error("州/県リストの読み込みエラー:", error));
    });
});
