document.addEventListener('DOMContentLoaded', function () {
    const provinceDropdown = document.getElementById('province');
    const cityDropdown = document.getElementById('city');
    const barangayDropdown = document.getElementById('barangay');

    const countryDropdown = document.getElementById('country'); 
    const postalCodeInput = document.getElementById('postal_code'); 

    // Fetch cities when a province is selected
     provinceDropdown.addEventListener('change', function () {
        const provinceCode = this.value;
        console.log(`Province selected: ${provinceCode}`); // Debugging
        if (provinceCode && provinceCode !== "void") {
            fetch(`/get_cities/${provinceCode}`)
                .then(response => response.json())
                .then(data => {
                    // Clear and populate the city dropdown
                    cityDropdown.innerHTML = '<option value="void">--Select the city--</option>';
                    data.cities.forEach(city => {
                        const option = document.createElement('option');
                        option.value = city.code;
                        option.textContent = city.name;
                        cityDropdown.appendChild(option);
                    });
                    barangayDropdown.innerHTML = '<option value="void">--Select the barangay--</option>'; // Reset barangay dropdown
                })
                .catch(error => console.error('Error fetching cities:', error)); // Debugging
        }
    });

    // Fetch barangays when a city is selected
    cityDropdown.addEventListener('change', function () {
        const cityName = cityDropdown.options[cityDropdown.selectedIndex].text;
        const countryCode = countryDropdown.value; // Should be ISO code like 'PH'
        const cityCode = this.value;
        console.log(`City selected: ${cityCode}`); // Debugging
        
        if (cityCode && cityCode !== "void") {
            fetch(`/get_barangays/${cityCode}`)
                .then(response => response.json())
                .then(data => {
                    // Clear and populate the barangay dropdown
                    barangayDropdown.innerHTML = '<option value="void">--Select the barangay--</option>';
                    data.barangays.forEach(barangay => {
                        const option = document.createElement('option');
                        option.value = barangay.code;
                        option.textContent = barangay.name;
                        barangayDropdown.appendChild(option);
                    });
                })
                .catch(error => console.error('Error fetching barangays:', error)); // Debugging
        }


        if (countryCode && cityName && countryCode !== "void" && cityName !== "--Select the city--") {
            fetch(`/get_postal_code?country_code=${countryCode}&city=${encodeURIComponent(cityName)}`)
                .then(response => response.json())
                .then(data => {
                    postalCodeInput.value = data.postal_code || '';
                })
                .catch(error => {
                    postalCodeInput.value = '';
                    console.error('Error fetching postal code:', error);
                });
        } else {
            postalCodeInput.value = '';
        }
    });
});