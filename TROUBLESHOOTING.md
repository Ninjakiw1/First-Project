# Troubleshooting

## "stream disconnected before completion: Your input exceeds the context window of this model"

This message comes from the language model API rather than the calendar application itself. It appears when a single request (prompt + any uploaded files or diffs) is larger than the model's maximum context size. To resolve the error:

1. **Shorten the prompt or files you send** – remove unnecessary commentary or split large diffs/documentation into smaller chunks before sending the next request to the model.
2. **Provide summaries instead of full files** – when you only need feedback on a part of a file, send just that section rather than the whole file.
3. **Use pagination for large diffs** – break the work into several smaller interactions (for example, one change per request) so each fits in the context window.
4. **Retry after pruning history** – if you are working inside a chat with a long history, start a new conversation or delete earlier turns so the model does not have to load as much context.

Following these steps keeps the payload within the model's context limit so responses complete without being truncated.
