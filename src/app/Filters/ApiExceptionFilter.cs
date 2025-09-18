using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;

namespace app.Filters;

public class ApiExceptionFilter : IExceptionFilter
{
    private readonly ILogger<ApiExceptionFilter> _logger;
    private readonly IHostEnvironment _env;

    public ApiExceptionFilter(
        ILogger<ApiExceptionFilter> logger,
        IHostEnvironment env)
    {
        _logger = logger;
        _env = env;
    }

    public void OnException(ExceptionContext context)
    {
        _logger.LogError(context.Exception, "An unhandled exception occurred");

        var apiError = new ApiErrorResponse
        {
            Type = context.Exception.GetType().Name,
            Message = context.Exception.Message
        };

        if (_env.IsDevelopment())
        {
            apiError.Detail = context.Exception.StackTrace;
        }

        context.Result = new ObjectResult(apiError)
        {
            StatusCode = context.Exception switch
            {
                InvalidWeatherForecastRequestException => StatusCodes.Status400BadRequest,
                _ => StatusCodes.Status500InternalServerError
            }
        };
    }
}

public class ApiErrorResponse
{
    public string Type { get; set; }
    public string Message { get; set; }
    public string Detail { get; set; }
}