document.addEventListener('DOMContentLoaded', function() {
    // Generate chart colors
    function generateChartColors(count) {
        const baseColors = [
            '#4dc9f6', '#f67019', '#f53794', '#537bc4', '#acc236',
            '#166a8f', '#00a950', '#8549ba', '#a4e43f', '#d6a4e3'
        ];
        
        if (count <= baseColors.length) {
            return baseColors.slice(0, count);
        }
        
        // If we need more colors than in our base array, generate them
        const colors = [...baseColors];
        for (let i = baseColors.length; i < count; i++) {
            const h = (i * 137) % 360; // Use golden ratio for even distribution
            colors.push(`hsl(${h}, 70%, 60%)`);
        }
        
        return colors;
    }
    
    // Investment preview calculation (for new investment form)
    const amountInput = document.getElementById('amount');
    const interestRateInput = document.getElementById('interest_rate');
    const yearsInput = document.getElementById('years');
    
    if (amountInput && interestRateInput && yearsInput) {
        const previewChartContainer = document.getElementById('preview-chart-container');
        const previewStats = document.getElementById('preview-stats');
        const previewInitial = document.getElementById('preview-initial');
        const previewFinal = document.getElementById('preview-final');
        const previewGrowth = document.getElementById('preview-growth');
        const previewAnnual = document.getElementById('preview-annual');
        
        // Chart instance
        let previewChart = null;
        
        // Update preview when inputs change
        const updateInputs = [amountInput, interestRateInput, yearsInput];
        updateInputs.forEach(input => {
            input.addEventListener('input', updatePreview);
        });
        
        function updatePreview() {
            const amount = parseFloat(amountInput.value) || 0;
            const interestRate = parseFloat(interestRateInput.value) || 0;
            const years = parseInt(yearsInput.value) || 0;
            
            if (amount > 0 && interestRate > 0 && years > 0) {
                // Show preview elements
                previewChartContainer.classList.remove('d-none');
                previewStats.classList.remove('d-none');
                
                // Calculate future value
                const futureValue = amount * Math.pow(1 + (interestRate / 100), years);
                const growthPercentage = ((futureValue - amount) / amount) * 100;
                const annualGrowth = interestRate; // Simplified, could be more complex
                
                // Update stats
                previewInitial.textContent = formatCurrency(amount);
                previewFinal.textContent = formatCurrency(futureValue);
                previewGrowth.textContent = formatPercentage(growthPercentage);
                previewAnnual.textContent = formatPercentage(annualGrowth);
                
                // Update chart
                updateChart(amount, interestRate, years);
            } else {
                // Hide preview elements if inputs are invalid
                previewChartContainer.classList.add('d-none');
                previewStats.classList.add('d-none');
            }
        }
        
        function updateChart(amount, interestRate, years) {
            // Generate data for each year
            const labels = [];
            const data = [];
            
            for (let year = 0; year <= years; year++) {
                labels.push(`Year ${year}`);
                const value = amount * Math.pow(1 + (interestRate / 100), year);
                data.push(Math.round(value * 100) / 100);
            }
            
            // Destroy previous chart if it exists
            if (previewChart) {
                previewChart.destroy();
            }
            
            // Create new chart
            const ctx = document.getElementById('preview-chart').getContext('2d');
            previewChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Investment Growth',
                        data: data,
                        fill: true,
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return '$' + value.toLocaleString();
                                },
                                color: 'white'
                            }
                        },
                        x: {
                            ticks: {
                                color: 'white'
                            }
                        }
                    }
                }
            });
        }
    }
    
    // Helper functions for formatting
    function formatCurrency(value) {
        return '$' + value.toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }
    
    function formatPercentage(value) {
        return value.toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }) + '%';
    }
});
