namespace app.Exceptions;

public class ApiException : Exception
{
    public ApiException() : base() { }
    public ApiException(string message) : base(message) { }
    public ApiException(string message, Exception innerException) : base(message, innerException) { }
}

public class InvalidWeatherForecastRequestException : ApiException
{
    public InvalidWeatherForecastRequestException(string message) : base(message) { }
}