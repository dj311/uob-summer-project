import scala.util.Try
import gremlin.scala._
import io.shiftleft.codepropertygraph.generated._
import java.nio.file.Paths
import io.shiftleft.queryprimitives.utils.ExpandTo
import org.apache.tinkerpop.gremlin.structure.Direction
import io.shiftleft.queryprimitives.steps.Implicits.JavaIteratorDeco
import javax.script.ScriptEngineManager
import scala.io.Source

/* APACHE from https://github.com/shiftleftsecurity/joern/ */
/* TODO: license properly */


/** Some helper functions: adapted from ReachingDefPass.scala in codeproperty graph repo */
def vertexToStr(vertex: Vertex, identifiers: Map[Vertex,Int]): String = {
  val str = new StringBuffer()

  str.append("id_")
  str.append(identifiers(vertex).toString)

  str.toString
}

def toProlog(graph: ScalaGraph): String = {
  var vertex_identifiers:Map[Vertex,Int] = Map()

  var index = 0
  graph.V.l.foreach{ v =>
    vertex_identifiers += (v -> index)
    index += 1
  }

  val buf = new StringBuffer()

  buf.append("% START: Generated Prolog\n")

  buf.append("% NODE PROPERTIES \n")
  graph.V.l.foreach{ v =>
    val vertex_str = vertexToStr(v, vertex_identifiers)

    Try {
      val node_name = v.value2(NodeKeys.NAME).toString

      node_name match {
        case "ALLOCA" =>
          buf.append("alloc(" + vertex_str + ").\n")
        case "malloc" =>
          buf.append("alloc(" + vertex_str + ").\n")
        case "memcpy" =>
          buf.append("writeToPointer(" + vertex_str + ").\n")
        case "memmove" =>
          buf.append("writeToPointer(" + vertex_str + ").\n")
        case "<operator>.sizeOf" =>
          buf.append("sizeOf(" + vertex_str + ").\n")
        case "<operator>.assignment" =>
          buf.append("assignment(" + vertex_str + ").\n")
        case "<operator>.computedMemberAccess" =>
          buf.append("compMemberAccess(" + vertex_str + ").\n")
      }
    }
  }
  
  buf.append("% METHOD \n")
  graph.V.l.foreach{ v =>
    val vertex_str = vertexToStr(v, vertex_identifiers)

    Try {
      val node_type = v.value2(NodeKeys.TYPE_FULL_NAME).toString
      node_type match{
        case "char * [ ]" =>
          buf.append("pointer(" + vertex_str + ").\n")
        case "size_t" =>
          buf.append("sizeOfInt(" + vertex_str + ").\n")
        case "int *" =>
          buf.append("pointer(" + vertex_str + ").\n")
        case "void" =>
          buf.append("voidPointer(" + vertex_str + ").\n")
        case "int [ 10 ]" =>
          buf.append("sizeOfInt(" + vertex_str + ").\n")
          buf.append("array10(" + vertex_str + ").\n")
      }

    }
  }

  buf.append("% CODE\n")
  graph.V.l.foreach{ v =>
    Try {
      buf.append(
        "source_code("
          + vertexToStr(v, vertex_identifiers)
          + ", \""
          + v.value2(NodeKeys.CODE).toString
          + "\")."
          + "\n"
      )
    }
  }

  buf.append("% AST\n")
  graph.E.hasLabel("AST").l.foreach { e =>
    val parentVertex = vertexToStr(e.outVertex, vertex_identifiers).replace("\"","\'")
    val childVertex = vertexToStr(e.inVertex, vertex_identifiers).replace("\"","\'")
    buf.append(s"""ast($parentVertex, $childVertex).\n """)
  }

  buf.append("% CFG\n")
  graph.E.hasLabel("CFG").l.foreach { e =>
    val parentVertex = vertexToStr(e.outVertex, vertex_identifiers).replace("\"","\'")
    val childVertex = vertexToStr(e.inVertex, vertex_identifiers).replace("\"","\'")
    buf.append(s"""cfg($parentVertex, $childVertex).\n """)
  }
  buf.append("% REF\n")
  graph.E.hasLabel("REF").l.foreach { e =>
    val parentVertex = vertexToStr(e.outVertex, vertex_identifiers).replace("\"","\'")
    val childVertex = vertexToStr(e.inVertex, vertex_identifiers).replace("\"","\'")
    buf.append(s"""ref($parentVertex, $childVertex).\n """)
  }

  buf.append("% END: Generated Prolog ")

  buf.toString
}

toProlog(cpg.graph)
