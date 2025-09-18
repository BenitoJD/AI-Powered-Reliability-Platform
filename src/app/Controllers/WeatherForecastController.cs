using Microsoft.AspNetCore.Mvc;
using app.Models;
using app.Exceptions;
using System.ComponentModel.DataAnnotations;

namespace app.Controllers;

[ApiController]
[Route("api/v1/[controller]")]
public class WeatherForecastController : ControllerBase
{
    private static readonly string[] Summaries = new[]
    {
        "Freezing", "Bracing", "Chilly", "Cool", "Mild", "Warm", "Balmy", "Hot", "Sweltering", "Scorching"
    };

    private readonly ILogger<WeatherForecastController> _logger;

    public WeatherForecastController(ILogger<WeatherForecastController> logger)
    {
        _logger = logger;
    }

    [HttpGet]
    [ProducesResponseType(typeof(IEnumerable<WeatherForecast>), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public ActionResult<IEnumerable<WeatherForecast>> Get()
    {
        try
        {
            _logger.LogInformation("Retrieving weather forecasts");
            
            var forecasts = Enumerable.Range(1, 5).Select(index =>
            {
                var forecast = new WeatherForecast
                {
                    Date = DateTime.UtcNow.AddDays(index),
                    TemperatureC = Random.Shared.Next(-20, 55),
                    Summary = Summaries[Random.Shared.Next(Summaries.Length)]
                };

                _logger.LogDebug("Generated forecast: {Date}, {Temperature}°C, {Summary}", 
                    forecast.Date, forecast.TemperatureC, forecast.Summary);

                return forecast;
            }).ToArray();

            _logger.LogInformation("Successfully retrieved {Count} weather forecasts", forecasts.Length);
            return Ok(forecasts);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error occurred while retrieving weather forecasts");
            return StatusCode(StatusCodes.Status500InternalServerError, 
                "An error occurred while processing your request. Please try again later.");
        }
    }

    [HttpGet("{days:int}")]
    [ProducesResponseType(typeof(IEnumerable<WeatherForecast>), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public ActionResult<IEnumerable<WeatherForecast>> Get([Range(1, 14, ErrorMessage = "Please request between 1 and 14 days of forecasts")] int days)
    {
        try
        {
            if (days <= 0 || days > 14)
            {
                throw new InvalidWeatherForecastRequestException($"Invalid number of days requested: {days}. Please request between 1 and 14 days.");
            }

            _logger.LogInformation("Retrieving weather forecasts for {Days} days", days);

            var forecasts = Enumerable.Range(1, days).Select(index =>
            {
                var forecast = new WeatherForecast
                {
                    Date = DateTime.UtcNow.AddDays(index),
                    TemperatureC = Random.Shared.Next(-20, 55),
                    Summary = Summaries[Random.Shared.Next(Summaries.Length)]
                };

                _logger.LogDebug("Generated forecast: {Date}, {Temperature}°C, {Summary}", 
                    forecast.Date, forecast.TemperatureC, forecast.Summary);

                return forecast;
            }).ToArray();

            _logger.LogInformation("Successfully retrieved {Count} weather forecasts", forecasts.Length);
            return Ok(forecasts);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error occurred while retrieving weather forecasts for {Days} days", days);
            return StatusCode(StatusCodes.Status500InternalServerError, 
                "An error occurred while processing your request. Please try again later.");
        }
    }
}
