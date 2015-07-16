# hansel

*Hansel, he's so hot right now*

Trying to add some simple domain validation without needing to subclass. Ideally the domain model shouldn't include any persistence logic or care whether it's driven by tornado, flask, or a CLI.

We'll see how it goes.

```python
class Question(Entity):
    id = UUID()
    text = Unicode()
    hint = Unicode()
    options = List('QuestionOption')

class QuestionService(Service):
  with Service.UL():
    question_id = UUID()
    option_id = UUID()
    created = Datetime()

  def foo(self, question_id, option_id, created):
    ...
```

The basic model validation is straight forward. What I'm wanting now is to automatically validate function arguments based on some ubiquitous language(UL). Within a service class it seems reasonable that certain variable names will always be a certain type. Right now this is attached to a concrete service class. Might be worthwhile to attach it to a bounded context and then have the service validate off of the BC.

Also feasible to validate all variable names within a BC and not just parameters.

Something I also want is to be able to reference `Question.id` and validate not just the type, but also whether a `UUID` for a `Question` entity. This would be more applicable within the domain model and not the boundary since at the application layer we'd just have to assume a valid `UUID` until we verify against some store. I'd rather not have to create a `UUID` subclass like `QuestionId(UUID)`.

## Ubiquitous Lanauge

One of the things I want is to do type checking via UL which essentially is a mapping of names to types. This could be applied to functions, classes, and modules.

With something like classes we could add a `strict` parameter that requires that all method parameters be typed via the `UL`. This would be useful for things like Service objects. Also, possible to hook into the import hooks and require that all instances of certain name be a certain type. It wouldn't need to be an actual `type` check though, we could use other invariants like `User's that are female`.

I would prefer a system like above the optional type checking syntax built into Python 3.
